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
import binascii
import time

from bluetooth.ble import BeaconService
from bluepy.btle import Scanner
from bluetooth import bluez
import MySQLdb #Modulo interazione DB 

RPI_ID = "rpi_1"

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
ID = "rpi_3"
PSW = "password_1"
DB_NAME = "devices_db"

ADV_DATA = ""
ADV_TIME = 15

UUID_DATA_STR = "rp1-salotto" # usare - per separare i campi
DASH_POS = [8, 13, 18, 23]
BEACON_SCAN_TIME = 15

"""
Classe che crea un oggetto device scansionato con tutti gli attributi necessari alla creazione
di un record nel database 
"""
class ScanedDevice:

    def __init__(self, name, addr, rssi, isBle):
        self.name = name
        self.addr = addr
        self.rssi = rssi
        self.isBle = isBle
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))

    def printData(self):
        print "%s - %s - %d at %s - %s " % (self.name, self.addr, self.rssi, self.date, self.time)

"""
Classe che crea un oggetto Beacon, in particolare un altro RPi che effettua la scansione 
in un'altra parte dell'ambiente
"""
class RPiBeacon:

    def __init__(self, data, addr, rssi):
        self.id, self.location = self._extractData(data)
        self.addr = addr
        self.rssi = rssi
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))

    def printData():
        print "%d - %s" % (self.id, self.location)

    def _extractData(data):

        for ch in ['-', "00"]:
            data = data.replace(ch, '')

        convStr = binascii.unhexlify(data)
        splitData = convStr.split('-')

        return splitData[0], splitData[1]


#Appende i dispositivi trovati nella lista devices
def scan_devices():

    devices = []

    print "Start scanning devices ..."
    os.system("sudo hciconfig hci0 down")
    os.system("sudo hciconfig hci0 up")
    
    scandevices = bluez.discover_devices(duration=SCAN_TIME, flush_cache=True, lookup_names=True, device_id=0)

    for scandevice in scandevices:
        for name, addr in scandevice.items():
            devices.append(ScanedDevice(name, addr, None, NOT_BLE))

    return devices 

#Appende i dispositivi BLE trovati nella lista devices
def lescan_devices():

    devices = []
    print "Start scanning LE devices ..."

    lescanner = Scanner()
    
    #Lista di oggetti bluepy.btle.ScanEntry
    ledevices = lescanner.scan(SCAN_TIME)

    #clean_dev = [[dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi] for dev in ledevices]
    #devices.append( ScanedDevice(dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi, IS_BLE) for dev in ledevices )

    for ledev in ledevices:
        devices.append(ScanedDevice(ledev.getValueText(COMPLETE_NAME), ledev.addr, ledev.rssi, IS_BLE))

    return devices

#Permette di identificare gli altri RPi Sniffer
def beaconScan():

    beacons = []

    service = BeaconService()
    devices = service.scan(BEACON_SCAN_TIME)

    for dev in devices:
        beacons.append(RPiBeacon(dev.getValueText(MANUFACTURER), dev.addr, dev.rssi))

    return beacons

def insertDash(string, pos):

    for x in pos:
        string = string[:x] + '-' + string[x:]

    return string

def uuidStrToHex(uuid_str, pos):

    convHex = binascii.hexlify(UUID_DATA_STR)

    #print convHex

    length = len(convHex)

    if length > 32:
        print "Error! Converted UUID is to long for standard"
    elif length < 32:
        convHex = convHex + "".join('0' for _ in range(32-len(convHex))) 

    uuid_hex = insertDash(convHex, pos)

    #print uuid_hex

    return uuid_hex    

"""
Funzione per permettere al RPi di essere identificato dagli altri sniffer, i dati di id, posizione
ed eventuali sono salvati nel byte del manufacturer rispettando le divisione dei caratteri HEX.
Una volta decodificati da HEX in STRING otteniamo i valori separati da un '-'
"""
def piAdv():

    service = BeaconService()
    service.start_advertising(uuidStrToHex(UUID_DATA_STR, DASH_POS), 1, 1, 1, 200)
    time.sleep(15)
    service.stop_advertising()

"""
Funzione per il caricamento dei dispositivi trovati nel database gestito da snifferBTserver.py
Permette anche l'aggiornamento dell'RSSI, data e orario dei record già esistenti.
"""
def load_devices(devices):
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    for dev in devices:
        rpi_id = RPI_ID
        dev.printData()
        try:
            cur.execute("INSERT INTO rpi_beacons(rpi_id, name, addr, rssi, date, time, is_ble) VALUES('%s', '%s', '%s', '%d', '%s', '%s', '%d')" % (rpi_id, dev.name, dev.addr, dev.rssi, dev.date, dev.time, dev.isBle)) 
        except MySQLdb.Error as e:
            if e[0] == 1062:
                cur.execute("UPDATE rpi_beacons SET rssi='%d', date='%s', time='%s';" % (dev.rssi, dev.date, dev.time) )

    db.commit()

    db.close()

    print "Loaded Data!"

def load_beacons(beacons):
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME, PORT)
    cur = db.cursor()

    for beacon in beacons:
        beacon.printData()
        try:
            cur.execute("INSERT INTO devices(id, location, addr, rssi, date, time) VALUES('%s', '%s', '%s', '%d', '%s', '%s')" % (beacon.id, beacon.location, beacon.addr, beacon.rssi, beacon.date, beacon.time)) 
        except MySQLdb.Error as e:
            if e[0] == 1062:
                cur.execute("UPDATE devices SET location='%s', rssi='%d', date='%s', time='%s';" % (beacon.location, beacon.rssi, beacon.date, beacon.time) )

    db.commit()

    db.close()

    print "Loaded Data!"

#if __init__ == "__main__":

while True:

    devices = []
    beacons = []

    #piAdv()

    #beacons = beaconScan()

    devices = scan_devices() + lescan_devices()

    load_devices(devices)
    load_beacons(beacons)

    time.sleep(SLEEP_BETWEEN_SCAN)
    






