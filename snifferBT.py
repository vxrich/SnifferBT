# coding=utf-8
'''
Sniffer BlueTooth per Raspberry Pi 3

Software che permette di catturare i pacchetti BlueTooth tramite una 
Raspberry Pi e ritornare i dati in un database che sarà aggiornato 
anche da altri dispositivi.
Il tutto per stimare la numero di persone presenti in un ambiente.
'''

#implementazione dello scanner BLE con BluePy e scanner non BLE con Bluez

import datetime
import os
import time

import binascii

from bluetooth.ble import BeaconService
import MySQLdb #Modulo interazione DB
import cPickle as pickle
from GATTServices import GATTServices

from constants import *
from client_query import *
from client_config import *

from Device import ScanedDevice, RPiBeacon


def getPassword():

    PSW = getpass.getpass()
    PSW_HASH = binascii.hexlify(PSW)


"""
Scan dei device con tool interni a linux, i risultati vengono poi filtrati per 
i dispositivi con nome risolvibile
"""
def hciScan():

    devices = []
    scandevices = []

    print "Start scanning devices ..."
    os.system("sudo hciconfig hci0 up")
    scandevices = os.popen("sudo btmgmt find").readlines()
    
    #Rimuovo le prime 2 righe generate e l'ultima, che sono generate da btmgmt
    scandevices.pop(0)
    scandevices.pop(0)
    scandevices.pop()

    #Unisce la riga del nome del dispositivo alla riga precedente contenente i dati relativi
    scandevices = scandevices[::2] 
    #Unisce le righe dello stesso dispositivo in un unica stringa
    scandevices = [i+j for i,j in zip(scandevices[::2],scandevices[1::2])] 

    for dev in scandevices:
        d = dev.split()
        try:
            devices.append(ScanedDevice(RPI_ID, ' '.join(d[d.index(TAG[0]):]), d[d.index(TAG[1])+1], d[d.index(TAG[2])], None, None)) 
        except ValueError:
            print "Impossible to find name of %s. It might not be scanned." % (d[d.index(TAG[1])+1])  
            print "Device deleted!"         
    
    #Per ogni dispositivo analizzo i servizi che offre e li salvo in una lista pulendoli da info non necessarie
    for dev in devices:
        extended_services = [(s.replace('Service Name: ', '')).replace('\n', '') for s in (os.popen('sdptool browse ' +dev.addr+ ' | grep "Service Name"').readlines())]
        
        service = [0 for _ in range(0,40)]

        for key,val in GATTServices:
            if val in extended_services:
                service[key] = 1

        dev.setServices(services)

    print "Scan completed!"
    print "-----------------------------------------------"

    return devices

"""
Scan dei dispositivi interni di linux senza filtrare i dati in modo da ottenere tutti i dispositivi 
presenti anche se mostrano solo l'indirizzo random
"""
def hciScanAll():

    devices = []
    scandevices = []

    print "Start scanning devices ..."
    os.system("sudo hciconfig hci0 up")
    scandevices = os.popen("sudo btmgmt find").readlines()
    
    #Rimuovo le prime 2 righe generate e l'ultima, che sono generate da btmgmt
    scandevices.pop(0)
    scandevices.pop(0)
    scandevices.pop()

    #Rimuovo le righe che iniziano con AD flags
    for i, lines in enumerate(scandevices):
        if "AD flags" in lines: 
            scandevices.pop(i)

    #Unisce le righe dello stesso dispositivo in un unica stringa
    scandevices = [i+j for i,j in zip(scandevices[::2],scandevices[1::2])] 

    print "########## SCAN DEVICES ##########"

    for dev in scandevices:
        d = dev.split()
        for t in range(0,len(d)):
            print d[t]
        print "-----------------------------------------------"

        try:
            devices.append(ScanedDevice(RPI_ID, ''.join(d[d.index(TAG[0])+1]), d[d.index(TAG[1])+1], d[d.index(TAG[2])+1], None, None)) 
        except ValueError:
            devices.append(ScanedDevice(RPI_ID, "RANDOM", d[d.index(TAG[1])+1], d[d.index(TAG[2])+1], None, None))     

    print "Scan completed!"
    print "-----------------------------------------------"

    return devices

#Permette di identificare gli altri RPi Sniffer
def beaconScan():

    beacons = []

    print "Scanning for other RPi .."

    service = BeaconService()
    devices = service.scan(BEACON_SCAN_TIME)

    for dev in devices:
        # beacons.append(RPiBeacon(dev.getValueText(MANUFACTURER), dev.addr, dev.rssi))
        beacons.append(RPiBeacon(devices[dev][0], dev, devices[dev][4]))

    load_obj([], beacons)

    print "Scan completed!"
    print "-----------------------------------------------"


def _insertDash(string, pos):

    for x in pos:
        string = string[:x] + '-' + string[x:]

    return string

def _uuidStrToHex(uuid_str, pos):

    convHex = binascii.hexlify(UUID_DATA_STR)

    #print convHex

    length = len(convHex)

    if length > 32:
        print "Error! Converted UUID is to long for standard"
    elif length < 32:
        convHex = convHex + "".join('0' for _ in range(32-len(convHex))) 

    uuid_hex = _insertDash(convHex, pos)

    #print uuid_hex

    return uuid_hex    

"""
Funzione per permettere al RPi di essere identificato dagli altri sniffer, 
i dati di id, posizione ed eventuali sono salvati nel byte del manufacturer 
rispettando le divisione dei caratteri HEX.
Una volta decodificati da HEX in STRING otteniamo i valori separati da un '-'
"""
def piAdv():

    print "Starting advertising .."
    service = BeaconService()
    service.start_advertising(_uuidStrToHex(UUID_DATA_STR, DASH_POS), 1, 1, 1, 200)
    time.sleep(15)
    service.stop_advertising()
    print "Advertising complete!"
    print "-----------------------------------------------"

"""
Funzione per il caricamento dei dispositivi trovati nel database gestito 
da snifferBTserver.py
Permette anche l'aggiornamento dell'RSSI, data e orario dei record già esistenti.
"""
def load_devices(devices):

    print "Loading devices' data on database .."
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    for dev in devices:
        dev.printData()
        try:
            cur.execute("INSERT INTO rpi_beacons(rpi_id, name, addr, rssi, date, time, is_ble) VALUES('%s', '%s', '%s', '%d', '%s', '%s', '%d')" % (dev.pi_id, dev.name, dev.addr, dev.rssi, dev.date, dev.time, dev.isBle)) 
        except MySQLdb.Error as e:
            if e[0] == 1062:
                cur.execute("UPDATE rpi_beacons SET rssi='%d', date='%s', time='%s';" % (dev.rssi, dev.date, dev.time) )

    db.commit()

    db.close()

    print "Loaded Data!"
    print "-----------------------------------------------"

"""
Funzione per caricare oggetti nel DB serializzandoli con Pickle
Carica sia gli oggetti ScanedDevice, sia gli oggetti RPiBeacon, 
ognuno nella tabella corretta.
"""
def load_obj(devices,beacons=[]):

    serialized_devices =[ pickle.dumps(dev) for dev in devices]
    serialized_beacons = [ pickle.dumps(beacon) for beacon in beacons]

    print "Loading devices' data on database .."
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    if len(serialized_devices) > 0:
        for dev in serialized_devices:
            try:
                cur.execute(INSERT_DEVICE % (dev)) 
            except MySQLdb.Error as e:
                print e
    else:
        print "No devices to load!"

    if len(serialized_beacons) > 0:        
        for beacon in serialized_beacons:
            try:
                cur.execute(INSERT_BEACON % (beacon)) 
            except MySQLdb.Error as e:
                print e
    else:
        print "No beacons to load!"

    db.commit()
    db.close()
    
    print "Loaded Serialized Object!"
    print "-----------------------------------------------"

"""
Funzione che carica sul DB nella tabella Rpi_beacon gli oggetti dei beacon 
scannerizzati.
"""
def load_beacons(beacons):

    print "Loading beacons' data on database .."
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    for beacon in beacons:
        beacon.printData()
        try:
            cur.execute("INSERT INTO devices(id, location, addr, rssi, date, time) VALUES('%s', '%s', '%s', '%d', '%s', '%s');" % (beacon.id, beacon.location, beacon.addr, beacon.rssi, beacon.date, beacon.time)) 
        except MySQLdb.Error as e:
            if e[0] == 1062:
                cur.execute("UPDATE devices SET location='%s', rssi='%d', date='%s', time='%s';" % (beacon.location, beacon.rssi, beacon.date, beacon.time) )

    db.commit()

    db.close()

    print "Loading complete!"
    print "-----------------------------------------------"

def scan():
    devices = []
    i=0
    while not devices and i < SCAN_LOOP:
        devices = hciScanAll()
        time.sleep(2)
        i += 1
            
    for dev in devices:
        dev.printData()


    # load_obj(devices, [])
    load_obj([dev for a in devices if dev.name == "L70"], [])

def command(arg):
    switcher={
        0: exit,
        1: piAdv,
        2: scan,
        3: beaconScan,
        }
    return switcher[int(arg)]()


while True:
    options = ["\n1 - Advertising", "2 - Scan", "3 - Beacon scan","0 - Uscita\n"]
    for opt in options:
        print opt

    choose = raw_input("Scegli un'opzione:")
    command(choose)








