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

from bluetooth.ble import BeaconService
from bluepy.btle import Scanner
from bluetooth import bluez
import MySQLdb #Modulo interazione DB 

WAITING_TIME = 120 #Secondi
SCAN_TIME = 10 #Secondi

COMPLETE_NAME = 0X09 #ID nome nell'oggetto ScanEntry
PUBLIC_TARGET_ADDRESS = 0X17
RANDOM_TARGET_ADDRESS = 0x18

#Dati per la connessione con il DataBase
HOST_NAME = "192.168.1.x"
ID = "rpi_1"
PSW = ""
DB_NAME = "devices_db"

ADV_DATA = ""

devices = []

"""
Classe che crea un oggetto device scansionato con tutti gli attributi necessari alla creazione
di un record nel database 
"""
class ScanedDevice:
    
    self.addr = ""
    self.name = ""
    self.rssi = None
    self.date = ""
    self.time = ""

    def _init_(self, name, addr, rssi):
        self.name = name
        self.addr = addr
        self.rssi = rssi
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time())

    def printData():
        print "%s - %s - %d at %s - %s " % (self.name, self.addr, self.rssi, self.date, self.time)
"""
Classe che crea un oggetto Beacon, in particolare un altro RPi che effettua la scansione 
in un'altra parte dell'ambiente
"""
class RPiBeacon:

    self.id = None
    self.location = ""

    def _init_(self, id, location):
        self.id = id
        self.location = location

    def printData():
        print "%d - %s" % (self.id, self.location)

#Appende i dispositivi trovati nella lista devices
def scan_devices():

    print "Start scanning devices ..."
    os.system("sudo hciconfig hci0 down")
    os.system("sudo hciconfig hci0 up")
    
    scandevices = bluez.discover_devices(duration=SCAN_TIME, flush_cache=True, lookup_names=True, device_id=0)

    devices.append(ScanedDevice(name, addr, None) for addr, name in scandevices.items())
    
    for dev in scandevices:
        dev.printData()

#Appende i dispositivi BLE trovati nella lista devices
def lescan_devices():

    print "Start scanning LE devices ..."

    #Lista di oggetti bluepy.btle.ScanEntry
    ledevices = lescanner.scan(SCAN_TIME)
    #clean_dev = [[dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi] for dev in ledevices]
    devices.append( ScanedDevice(dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi) for dev in ledevices )

    for dev in devices:
        dev.printData()
    

def piAdv():

    service = BeaconService()
    service.start_advertising(ADV_DATA)


def load_data(devices):

    date = str(datetime.datetime.now().date())
    time = str(datetime.datetie.now().time())
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME)
    cur = db.cursor()

    for dev in devices:
        cur.execute("INSERT INTO devices(name, addr, rssi, date, time) VALUES(%s, %s, %d, %s, %s)" % (dev.name, dev.addr, dev.rssi, dev.date, dev.time)) 

    db.commit()
    db.close

lescanner = Scanner()

while True:

    scan_devices()
    lescan_devices()

    load_data()
    






