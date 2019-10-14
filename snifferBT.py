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
import time

#from bluetooth.ble import BeaconService
from bluepy.btle import Scanner
from bluetooth import bluez
import MySQLdb #Modulo interazione DB
import cPickle as pickle
from GATTServices import GATTServices

from Device import ScanedDevice, RPiBeacon

RPI_ID = "rpi_1"
#Sfruttiamo l'UUID per inviare nome-locale-posizionex-posizioney
UUID_DATA_STR = "rp_1-salotto-x-y" # usare - per separare i campi

TAG = ["name", "dev_found", "rssi"]

WAITING_TIME = 120 #Secondi
SCAN_TIME = 10 #Secondi 
SLEEP_BETWEEN_SCAN = 300

# Trovi questi parametri https://github.com/IanHarvey/bluepy/blob/master/bluepy/btle.py
COMPLETE_NAME = 0X09 #ID nome nell'oggetto ScanEntry
PUBLIC_TARGET_ADDRESS = 0X17
RANDOM_TARGET_ADDRESS = 0x18
MANUFACTURER = 0xFF

IS_BLE = 1
NOT_BLE = 0

#Dati per la connessione con il DataBase
HOST_NAME = "192.168.1.15"
PORT = 3306
ID = RPI_ID
PSW = "password_1"
DB_NAME = "devices_db"

ADV_DATA = ""
ADV_TIME = 15

DASH_POS = [8, 13, 18, 23]
BEACON_SCAN_TIME = 15

INSERT_DEVICE = 'INSERT INTO serial_device(device_obj) VALUES("%s")'
INSERT_BEACON = 'INSERT INTO serial_beacon(beacon_obj) VALUES("%s");'

def getPassword():

    PSW = getpass.getpass()
    PSW_HASH = binascii.hexlify(PSW)


#Scan dei device con tool interni a linux
def hciscan():

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
    scandevices = scandevices[::2] #elimina la riga AD flags
    scandevices = [i+j for i,j in zip(scandevices[::2],scandevices[1::2])] #Unisce le righe dello stesso dispositivo in un unica stringa

    for dev in scandevices:
        d = dev.split()
        try:
            devices.append(ScanedDevice(RPI_ID, ' '.join(d[d.index(TAG[0]):]), d[d.index(TAG[1])+1], d[d.index(TAG[2])], None, None)) 
        except ValueError:
            print "Impossible to find name of %s. It might not be scanned."   
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

#Permette di identificare gli altri RPi Sniffer
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
Funzione per permettere al RPi di essere identificato dagli altri sniffer, i dati di id, posizione
ed eventuali sono salvati nel byte del manufacturer rispettando le divisione dei caratteri HEX.
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
Funzione per il caricamento dei dispositivi trovati nel database gestito da snifferBTserver.py
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
Carica sia gli oggetti ScanedDevice, sia gli oggetti RPiBeacon, ognuno nella tabella corretta
"""
def load_obj(devices,beacons):

    serialized_devices =[ pickle.dumps(dev) for dev in devices]
    serialized_beacons = [ pickle.dumps(beacon) for beacon in beacons]

    print "Loading devices' data on database .."
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    for dev in serialized_devices:
        try:
            cur.execute(INSERT_DEVICE % (dev)) 
        except MySQLdb.Error as e:
            print e
            
    for beacon in serialized_beacons:
        try:
            cur.execute(INSERT_BEACON % (beacon)) 
        except MySQLdb.Error as e:
            print e

    db.commit()
    db.close()
    
    print "Loaded Serialized Object!"
    print "-----------------------------------------------"

"""
Funzione che carica sul DB nella tabella Rpi_beacon gli oggetti dei beacon scannerizzati
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

#if __init__ == "__main__":

while True:

    devices = []
    beacons = []

    #piAdv()

    #beacons = beaconScan()
     
    # devices = scan_devices() + lescan_devices()
    i = 0

    #Se dopo lo scan la lista è vuota aspetta 10 secondi e riprova a effettuare lo scan
    while not devices and i < 2:
        devices = hciscan()
        time.sleep(10)
        i += 1
         

    for dev in devices:
        dev.printData()

    #load_devices(devices)
    #load_beacons(beacons)
    
    load_obj(devices, beacons)

    time.sleep(SLEEP_BETWEEN_SCAN)







