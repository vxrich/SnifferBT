# coding=utf-8
'''
Sniffer BlueTooth per Raspberry Pi 3

Software che permette di catturare i pacchetti BlueTooth tramite una Raspberry Pi e ritornare i dati 
in un database che sarà aggiornato anche da altri dispositivi.
Il tutto per stimare la numero di persone presenti in un ambiente.

'''

from bluetooth.ble import DiscoveryService #Modulo per scanning dei device
from bluetooth.ble import BeaconService #Modulo per effettuare advertising da parte del Raspberry 
import time

serviceDS = DiscoveryService()
serviceBS = BeaconService()
devices = service.discover(2)

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
