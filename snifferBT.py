# coding=utf-8
'''
Sniffer BlueTooth per Raspberry Pi 3

Software che permette di catturare i pacchetti BlueTooth tramite una Raspberry Pi e ritornare i dati 
in un database che sarà aggiornato anche da altri dispositivi.
Il tutto per stimare la numero di persone presenti in un ambiente.

'''

#Questo codice trova il telefono sia da RPi sia da MiNotebook (Funziona una volta poi non funziona più)

from bluetooth import bluez #Modulo base per l'interazione bluetooth 
from bluetooth import ble #Modulo per lo scanning BLE
import MySQLdb #Modulo interazione DB 

WAITING_TIME = 120 #Secondi

HOSTNAME = ""
ID = ""
PSW = ""
DB_NAME = ""

LOAD_QUERY = ""

#db = MySQLdb.connect(HOST, ID, PSW, DB_NAME)
#cur = db.cursor()


def scan_devices():

    print "Start scanning devices ..."
    
    devices = bluez.discover_devices(duration=2, flush_cache=True, lookup_names=True)
    #devices = ble.discover_devices()

    print "Printing Data ..."

    return devices

def print_devices(devices):

    for address, name in devices.items():
        print("name: {}, address: {}".format(name, address))

def load_data():
    
    cur.execute(LOAD_QUERY)


while True:

    scan_devices()

    load_data()
    






