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

from bluetooth.ble import BeaconService
from bluepy.btle import Scanner
from bluetooth import bluez
import MySQLdb #Modulo interazione DB 

RPI_ID = "rpi_1"

WAITING_TIME = 120 #Secondi
SCAN_TIME = 10 #Secondi

COMPLETE_NAME = 0X09 #ID nome nell'oggetto ScanEntry
PUBLIC_TARGET_ADDRESS = 0X17
RANDOM_TARGET_ADDRESS = 0x18
MANUFACTURER = 0xFF

#Dati per la connessione con il DataBase
HOST_NAME = "192.168.1.x"
ID = "rpi_1"
PSW = ""
DB_NAME = "devices_db"

ADV_DATA = ""
ADV_TIME = 15

UUID_DATA_STR = "" # usare - per separare i campi
DASH_POS = [8, 13, 18, 23]
BEACON_SCAN_TIME = 15

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
    self.addr = ""
    self.location = ""
    self.rssi = None

    def _init_(self, data, addr):
        self.id, self.location = self._extractData(data)
        self.addr = addr

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

def insertDash(string, pos):

    for x in pos:
        string[:index] + '-' + string[index:]

    return string

def uuidStrToHex(uuid_str, pos):

    convHex = binascii.hexlify(UUID_DATA_STR)

    lenght = len(convHex)

    if lenght > 32:
        print "Error! Converted UUID is to long for standard"
    elif lenght < 32:
        convHex = convHex + ('0' * 32-lenght) 

    uuid_hex = insertDash(convHex, pos)

    return uuid_hex    

def piAdv():

    service = BeaconService()
    service.start_advertising(uuidStrToHex(UUID_DATA_STR, DASH_POS), 1, 1, 1, 200)
    time.sleep(15)
    service.stop_avertising()

def beaconScan():

    service = BeaconService()
    devices = service.scan(BEACON_SCAN_TIME)

    for address, data in list(devices.items()):
        b = RPiBeacon(data, address)
        print(b)

def load_data(devices):

    date = str(datetime.datetime.now().date())
    time = str(datetime.datetie.now().time())
    
    db = MySQLdb.connect(HOST_NAME, ID, PSW, DB_NAME)
    cur = db.cursor()

    for dev in devices:
        rpi_id = RPI_ID
        cur.execute("INSERT INTO devices(name, addr, rssi, date, time) VALUES(%s, %s, %s, %d, %s, %s)" % (rpi_id, dev.name, dev.addr, dev.rssi, dev.date, dev.time)) 

    db.commit()
    db.close

lescanner = Scanner()

while True:

    piAdv()
    scan_devices()
    lescan_devices()

    load_data()
    






