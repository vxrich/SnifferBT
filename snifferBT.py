# coding=utf-8
'''
Sniffer BlueTooth per Raspberry Pi 3

Software che permette di catturare i pacchetti BlueTooth tramite una Raspberry Pi e ritornare i dati 
in un database che sarà aggiornato anche da altri dispositivi.
Il tutto per stimare la numero di persone presenti in un ambiente.

'''

#implementazione dello scanner BLE con BluePy e scanner non BLE con Bluez

import datetime
import os

from bluepy.btle import Scanner
from bluetooth import bluez
import MySQLdb #Modulo interazione DB 

WAITING_TIME = 120 #Secondi
SCAN_TIME = 10 #Secondi

HOSTNAME = ""
ID = ""
PSW = ""
DB_NAME = ""

LOAD_QUERY = ""

#db = MySQLdb.connect(HOST, ID, PSW, DB_NAME)
#cur = db.cursor()


def scan_devices():

    print "Start scanning devices ..."
    
    

    print "Printing Data ..."

    return devices

def lescan_devices():

    print "Start scanning LE devices ..."

    #Lista di oggetti bluepy.btle.ScanEntry
    ledevices = lescanner.scan(SCAN_TIME)

    print "Printing data ..."
    for dev in devices:
        
        print "%s - %s - %d" % (dev.name, dev.addr, dev.rssi)

    
    return devices

def print_devices(devices):

    for address, name in devices.items():
        print("name: {}, address: {}".format(name, address))

def load_data():
    
    cur.execute(LOAD_QUERY)


lescanner = Scanner()

while True:

    scan_devices()

    load_data()
    






