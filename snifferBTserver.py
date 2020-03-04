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

import random

import datetime 
import os
import MySQLdb
import time
from datetime import datetime
import warnings
import cPickle as pickle
from itertools import combinations, groupby
from collections import defaultdict

from Device import ScanedDevice, RPiBeacon
from GATTServices import GATTServices

from scipy.spatial.distance import euclidean as dist
import numpy as np
from numpy.linalg import solve
from tempfile import TemporaryFile      

# import matplotlib.pyplot as plt

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

    for query in QUERIES:
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

def deleteDatabase():
    choose = raw_input("Sei sicuro di voler cancellare il databse? (y,n)")
    if choose.lower() == "y":
        db = MySQLdb.connect(HOST_NAME, ID, PSW)
        cur = db.cursor()
        cur.execute(USE_DB)
        cur.execute(DELETE_DEV_TABLE)
        cur.execute(CREATE_TABLE_SERIALIZE_DEVICE)
        return 0
    else:
        return 0

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

    groups = defaultdict(list)
    for dev in rows:
        groups[dev.addr].append(dev)
    devices = groups.values()

    for dev in devices:
        for d in dev:
            d.printData()

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
    cur.execute(SELECT_ALL_SER_DEV)
    fetch = cur.fetchall()
    devices = deserialize_devices(fetch)
    devices.sort(key=lambda x: x.addr)

    for d in devices:
        d.printData()

    #Fetch dei RPiBeacon
    # cur.execute(SELECT_ALL_BEACON)
    # fetch = cur.fetchall()
    # beacons = deserialize_devices(fetch)
    beacons = [ RPiBeacon(b['uuid'], b['addr'], b['rssi'] ) for b in CONST_BEACON ]

    #Raggruppo i dispositivi per MAC address
    groups = defaultdict(list)
    for dev in devices:
        groups[dev.addr].append(dev)
    devices = groups.values()

    # for d in devices: 
    #     for t in d:
    #         t.printData()
    #     print "########################"

    clean_dev = []
    #I devices sono raggruppati per addr, quindi dev è una lista
    for dev in devices:
        if len(dev) < 3:
            print "Device %s is not found by all the RPi Beacon" % (dev[0].addr)
        else:
            #Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
            dev_cp = []
            circ = []
            
            #Filtro i dispositivi se trovo più una entry  per dispositivo faccio una media e ne riposto uno solo
            dev_group = defaultdict(list)
            if len(dev) > 3:
                for d in dev:
                    dev_group[d.rpi_id].append(d)
                # dev = dev_groups.values()
                dev = []
                for key in dev_group:
                    if len(dev_group[key]) > 1:
                        dev.append(ScanedDevice(key,dev_group[key][0].name,dev_group[key][0].addr, sum(x.distance for x in dev_group[key])/len(dev_group[key]) ))
                    else:
                        dev.append(dev_group[key][0])

            #Viene preso un dispositivo alla volta e confrontato con i RPiBeacon che ho, al corrispondete viene calcolata la 
            #circonferenza con centro RPiBeacon e raggio la distanza alla quale viene trovato il Device
            for d in dev:    
                for b in beacons:
                    if d.rpi_id == b.rpi_id:
                        dev_cp.append((d,b)) 
                        z = b.x**2 + b.y**2 - d.distance**2 #
                        circ.append(np.array([-b.x*2,-b.y*2,z])) #Ottengo le componenti utili del'eq della circonferenza che corrispondo a ax+by+c 
                        print "CIRCONFERENZA ==> ", b.rpi_id,-b.x*2,-b.y*2,z, d.distance

            #Effettuo il prodotto cartesiano tra le circonferenze trovate in modo che nel calcolo delle eq trovo facilemente
            #la retta che congiunge i 2 punti di tangenza tra le circonfereze
            circ_cp = combinations(circ,2) 

            # fig, ax = plt.subplots()
            # plt.xlim(-20,20)
            # plt.ylim(-20,20)
            # ax.set_aspect(1)
            # for c in circ:
            #     circle1 = plt.Circle((c[0], c[1]), c[2], color=random.choice("rgb"))
            #     ax.add_artist(circle1)
            # fig.savefig('plotcircles.png')
            # plt.show()

            lines = []
            #Calcolo della retta fra due circonferenze sottraendo i termini trovati, corrispondenti agli ultimi 3 termini dell'eq
            #della circonferenza. 
            
            for a,b in circ_cp:
                print "CIRC ==>", a,b
                line = np.subtract(a,b)
                #lin_eq[2]= lin_eq[2]/2
                lines.append(line)

            # Per trovare l'intersezione utilizzo la funzione di risoluzione dei sistemi lineari
            # di numpy, prima pero' devo costruire la matrice A e b
            # Le matrici A e b sono riferite a solo 2 rette, perchè per costruzione l'intersezione 
            # delle altre sare lo stesso punto

            # print "LINES ==>", lines
            l = []
            for line in lines:
                if line[0] != 0 and line[1] != 0:
                    l.append(line)
            lines = l
            print "LINES ==>", lines

            A = np.array([(lines[0])[0:2], (lines[1])[0:2]])
            b = np.array([-(lines[0])[2],-(lines[1])[2]])
            print "MATRIX ==>", A,b
            
            # points conterrá elementi del tipo np.array
            try:
                point = np.linalg.solve(A,b)
            except np.linalg.LinAlgError as err:
                print " MATRICE SINGOLARE PER %s, %s" % (dev[0].name, dev[0].addr)
                point = np.array([0,0])

            print "PUNTO ==>", point, dev[0].addr, dev[0].name

            #Setto la posizione solo al primo dei 3 trovati e lo salvo nei device trovati in modo da non avere 
            # duplicati
            dev[0].setPosition(point[0],point[1])
            clean_dev.append(dev[0])
        
            filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            np.save(filename,[lines, circ, point])

        print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

    for d in clean_dev:
        d.printData()

    # #Trovare il numerp di persone in base alla posizione dei dispositivi.
    # #09/10/19
    # #Difficile classificare i dispositivi con questa accuratezza per problemi di SDP
    # count = len(clean_dev)
    # for d in clean_dev:
    #     for d1 in clean_dev:
    #         if d.addr != d1.addr or dist(d.position,d1.position) < 1.5:
    #             if d.type == d1.type == "SMARTPHONE":
    #                 pass
    #             elif d.type == "SMARTPHONE" and d1.type == "SMARTBAND":
    #                 count -= 1
    #             elif d.type == "SMARTPHONE" and d1.type == "SMARTBAND":
    #                 pass

    # print "##################################"
    # print "  FOUND &d PERSONS IN THIS AREA!" % (count)
    # print "##################################"


def command(arg):
    switcher={
        0: exit,
        1: printData,
        2: deleteDatabase,
        3: dbStartUp,
        4: evaluationData,
        }
    return switcher[int(arg)]()


os.system("sudo service mysql restart")
# dbStartUp()

while True:
    options = ["\n1 - Stampa il database", "2 - Cancella il database", "3 - Database Startup","4 - Evaluate", "0 - Uscita\n"]
    for opt in options:
        print opt

    choose = raw_input("Scegli un'opzione:")
    command(choose)



# dbStartUp()
# """
# while True:

#     #rpi_beacons = beaconScan()
#     #printData()
#     #evaluationData()
#     time.sleep(30)
# """
# printData()
# #evaluationData()

