#coding=utf-8
"""
Sniffer Bluetooth server, crea il DB e gli users, 

Dati Database:
Name = devices_db
Table = devices(rpi_id, name, addr, rssi, date, time)

Se all'avvio appare l'errore 2002 
sudo service mysql restart

In un nuovo ambiente è necessario creare gli USERS per loggarsi in mysql:
CREATE USER 'nome'@'localhost' IDENTIFIED BY 'nome';
GRANT ALL PRIVILEGES ON *.* TO 'nome'@'localhost';
"""
from __future__ import division
from bluetooth.ble import BeaconService

import datetime
import os
import MySQLdb
import time
import warnings
import cPickle as pickle
from scipy.spatial.distance import euclidean as dist
from itertools import combinations, groupby
from collections import defaultdict
from Device import ScanedDevice, RPiBeacon, Circle
import numpy as np
from numpy.linalg import solve

# Permette di catturare nei try/except i warnings come se fossero errori in modo
# da gestirli meglio
warnings.filterwarnings('error', category=MySQLdb.Warning)

# C'è da creare un user mysql prima di avviare il programma oppure lo si crea direttamente
# da qui dentro connettendosi da root
HOST_NAME = "localhost"
ID = "root"
PSW = "asusx205ta"
DB_NAME = "devices_db"

rpi_users = [
    ("rpi_1", "192.168.1.1", "password_1"),
    ("rpi_2", "192.168.1.3", "password_2"),
    ("rpi_3", "192.168.1.15", "password_1")
]

rpi_beacons =[]

CREATE_DB = "CREATE DATABASE IF NOT EXISTS devices_db"
USE_DB = "USE devices_db"

CREATE_TABLE_SERIALIZE_DEVICE = "CREATE TABLE IF NOT EXISTS serial_device (device_obj varchar(500))"
CREATE_TABLE_SERIALIZE_BEACON = "CREATE TABLE IF NOT EXISTS serial_beacon (beacon_obj varchar(500))"
CREATE_TABLE_DEVICE = "CREATE TABLE IF NOT EXISTS device (rpi_id varchar(10), name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(8), PRIMARY KEY(rpi_id, addr))"
CREATE_TABLE_BEACON = "CREATE TABLE IF NOT EXISTS rpi_beacon (id varchar(10) PRIMARY KEY, location varchar(15), addr varchar(17), rssi int(4), date varchar(12), time varchar(8));"

fromGRANT = "GRANT PREVILEGES ON *.* TO '%s'"

queries = [CREATE_DB, USE_DB, CREATE_TABLE_BEACON, CREATE_TABLE_DEVICE, CREATE_TABLE_SERIALIZE_DEVICE, CREATE_TABLE_SERIALIZE_BEACON]

"""
dbStartUp()
Permette di inizializzare il database con le strutture necessarie all'archiviazione dei dati ottenuti da snifferBT.py
Le strutture che crea verificando che non siano già presenti sono:
- DB
- Table serial_dev --> Per lo store degli oggetti serializzati
- Table devices --> Per lo store dei dati degli oggetti in versione non serializzata
- Table rpi_beacons --> Per lo store dei dati degli altri snifferBT 
Inoltre crea gli utenti definiti nella lista rpi_users e garantisce loro tutti i permessi sulla base di dati
"""
def dbStartUp():
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()

    for query in queries:
        try:
            cur.execute(query)
        except MySQLdb.Warning:
            print "Query already satisfied!"

    for user in rpi_users:
        try:
            cur.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))
        except MySQLdb.Warning:
            print "User %s is already created!" % (user[0])    
        cur.execute("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))
    
    cur.execute("FLUSH PRIVILEGES;")

    db.commit()
    db.close()

def printData():
    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()
    
    cur.execute(USE_DB)

    print "--------------------------"
    
    cur.execute("SELECT * FROM devices")
    rows = cur.fetchall()

    for row in rows:
        print row

    db.commit()
    db.close()

"""
Permette di identificare gli altri RPi Sniffer, in modo da costruire i riferimenti per
triangolare i device scansionati.
"""
def beaconScan():

    beacons = []

    print "Scanning for other RPi .."

    service = BeaconService()
    devices = service.scan(BEACON_SCAN_TIME)

    for dev in devices:
        beacons.append(RPiBeacon(dev.getValueText(MANUFACTURER), dev.addr, dev.rssi))

    print "Scan completed!"
    print "-----------------------------------------------"


    return beacons

def deserialize_devices(devices):

    return [ pickle.loads(dev[0]) for dev in devices ]

# Funzione che prende in input due circonferenze, identificate da centro e raggio
# e ritorna i punti di intersezione
# NECESSARIO IMPLEMENTAZIONE DEI NOMI CORRETTI
#def intersection(A, b):
    

#Metodo che permette di stimare le persone nell'area scansionata
def evaluationData():

    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()
    
    cur.execute(USE_DB)

    #Fetch dei device scansionati
    cur.execute("SELECT * FROM serial_dev;")
    fetch = cur.fetchall()
    devices = deserialize_devices(fetch)
    devices.sort(key=lambda x: x.addr)

    #Fetch dei RPiBeacon
    cur.execute("SELECT * FROM serial_beacon;")
    fetch = cur.fetchall()
    beacons = deserialize_devices(fetch)

    #Raggruppo i dispositivi per MAC address
    groups = defaultdict(list)
    for dev in devices:
        groups[dev.addr].append(dev)
    devices = groups.values()

    
    #I devices sono raggruppati per addr, quindi dev è una lista
    for dev in devices:
        if len(dev) < 3:
            print "Device %s is not found by all the RPi Beacon"
        else:
            points = []
            #Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
            dev_cp = []
            vects = []
            for d in dev:
                for b in beacons:
                    if d.rpi_id == b.rpi_id:
                        dev_cp.append((d,b)) 
                        z = b.x**2 + b.y**2 - d.distance**2
                        vects.append(np.array([b.x*2,b.y*2,z])) # Calcolo solo la terza riga della matice perchè le altre non sevono

                vects_cp = combinations(mat,2)
                lin_eqs = []
                """
                Prendo le combianzioni lineari delle matrici delle circonferenze e le sottraggo 
                per ottenere le rette secanti i 2 punti di intersezione tra le coppie di circonferenze
                con la matrice delle rette troverò il punto di intersezione di quest'ultime.
                Questo metodo mi permette di trovare un punto anche con misurazioni imprecise
                In questo modo è possibile intersecare anche solo 2 rette e si trova il punto 

                Necessario implementare controllo sulla lunghezza dei raggi nel caso 2 circonferenze non si
                toccano
                """
                for a,b in vects_cp:
                    lin_eq = np.subtract(a,b)
                    #lin_eq[2]= lin_eq[2]/2
                    lin_eqs.append(lin_eq)

                # Per trovare l'intersezione utilizzo la funzione di risoluzione dei sistemi lineari
                # di numpy, prima però devo costruire la matrice A e b
                # Le matrici A e b sono riferite a solo 2 rette, perchè per costruzione l'intersezione 
                # delle altre sarà lo stesso punto
                A = np.array([(lin_eqs[0])[0:2], (lin_eqs[1])[2])
                b = np.array([(lin_eqs[0])[2],(lin_eqs[1])[2])
                # points conterrà elementi del tipo np.array
                points.append(np.solve(A,b))




os.system("sudo service mysql restart")

dbStartUp()
"""
while True:

    #rpi_beacons = beaconScan()
    #printData()
    #evaluationData()
    time.sleep(30)
"""