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
# from bluetooth.ble import BeaconService

import datetime 
import os
import MySQLdb
import time
import warnings
import cPickle as pickle
from scipy.spatial.distance import euclidean as dist
from itertools import combinations, groupby
from collections import defaultdict
from Device import ScanedDevice, RPiBeacon
import numpy as np
from numpy.linalg import solve
from GATTServices import GATTServices

from server_query import *
from server_config import *

# Permette di catturare nei try/except i warnings come se fossero errori in modo
# da gestirli meglio
warnings.filterwarnings('error', category=MySQLdb.Warning)

rpi_beacons =[]

MAX_DISTANCE = 1.5


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
            cur.execute(CREATE_USER % (user[0], user[1], user[2]))
        except MySQLdb.Warning:
            print "User %s is already created!" % (user[0])    
        cur.execute(GRANT_PRIVILEGES % (user[0], user[1]))
        cur.execute(ALTER_USER % (user[0], user[1], user[2]))
    cur.execute(FLUSH)

    db.commit()
    db.close()

def printData():
    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()
    
    cur.execute(USE_DB)

    print "############### DEVICES ###############"
    
    cur.execute(SELECT_ALL_DEV)
    rows = cur.fetchall()

    for row in rows:
        print row

    print "############### SERIAL DEVICES ###############"

    cur.execute(SELECT_ALL_SER_DEV)
    rows = deserialize_devices(cur.fetchall())

    for dev in rows:
        dev.printData()

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
    cur.execute(SELECT_ALL_DEV)
    fetch = cur.fetchall()
    devices = deserialize_devices(fetch)
    devices.sort(key=lambda x: x.addr)

    #Fetch dei RPiBeacon
    cur.execute(SELECT_ALL_BEACON)
    fetch = cur.fetchall()
    beacons = deserialize_devices(fetch)

    #Raggruppo i dispositivi per MAC address
    groups = defaultdict(list)
    for dev in devices:
        groups[dev.addr].append(dev)
    devices = groups.values()

    clean_dev = []
    #I devices sono raggruppati per addr, quindi dev è una lista
    for dev in devices:
        if len(dev) < 3:
            print "Device %s is not found by all the RPi Beacon"
        else:
            #Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
            dev_cp = []
            circ = []
        
            #Viene preso un dispositivo alla volta e confrontato con i RPiBeacon che ho, al corrispondete viene calcolata la 
            #circonferenza con centro RPiBeacon e raggio la distanza alla quale viene trovato il Device
            for d in dev:    
                for b in beacons:
                    if d.rpi_id == b.rpi_id:
                        dev_cp.append((d,b)) 
                        z = b.x**2 + b.y**2 - d.distance**2 #
                        circ.append(np.array([b.x*2,b.y*2,z])) #Ottengo le componenti utili del'eq della circonferenza che corrispondo a ax+by+c 
                        #print b.rpi_id,b.x*2,b.y*2,z, d.distance

            #Effettuo il prodotto cartesiano tra le circonferenze trovate in modo che nel calcolo delle eq trovo facilemente
            #la retta che congiunge i 2 punti di tangenza tra le circonfereze
            circ_cp = combinations(circ,2) 

            lines = []
            #Calcolo della retta fra due circonferenze sottraendo i termini trovati, corrispondenti agli ultimi 3 termini dell'eq
            #della circonferenza. 
            
            for a,b in circ_cp:
                line = np.subtract(a,b)
                #lin_eq[2]= lin_eq[2]/2
                lines.append(line)

            # Per trovare l'intersezione utilizzo la funzione di risoluzione dei sistemi lineari
            # di numpy, prima pero' devo costruire la matrice A e b
            # Le matrici A e b sono riferite a solo 2 rette, perchè per costruzione l'intersezione 
            # delle altre sare lo stesso punto

            #print lines

            A = np.array([(lines[0])[0:2], (lines[2])[0:2]])
            b = np.array([(lines[0])[2],(lines[2])[2]])
            
            # points conterrá elementi del tipo np.array
            point = np.linalg.solve(A,b)

            #Setto la posizione solo al primo dei 3 trovati e lo salvo nei device trovati in modo da non avere 
            # duplicati
            dev[0].setPosition(point[0],point[1])
            clean_dev.append(dev[0])

    for d in clean_dev:
        d.printData()

    #Trovare il numerp di persone in base alla posizione dei dispositivi.
    #09/10/19
    #Difficile classificare i dispositivi con questa accuratezza per problemi di SDP
    count = len(clean_dev)
    for d in clean_dev:
        for d1 in clean_dev:
            if d.addr != d1.addr or dist(d.position,d1.position) < 1.5:
                if d.type == d1.type == "SMARTPHONE":
                    pass
                elif d.type == "SMARTPHONE" and d1.type == "SMARTBAND":
                    count -= 1
                elif d.type == "SMARTPHONE" and d1.type == "SMARTBAND":
                    pass

    print "##################################"
    print "  FOUND &d PERSONS IN THIS AREA!" % (count)
    print "##################################"



os.system("sudo service mysql restart")

dbStartUp()
"""
while True:

    #rpi_beacons = beaconScan()
    #printData()
    #evaluationData()
    time.sleep(30)
"""
printData()
#evaluationData()

