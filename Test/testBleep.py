from bluetooth import *
from bleep import BLEDevice
import datetime

print "-- Test Bleep Interface --"
print "Start scanning devices ..."

while True:
        print datetime.datetime.now()   
        
        devices = BLEDevice.discoverDevices(device='hci0', timeout=5)

        for device in devices:
                print device

        print "--------------------------------------------------------------------"

#for address, name in devices.items():
#        print("name: {}, address: {}".format(name, address))