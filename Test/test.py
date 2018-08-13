from bluetooth import bluez
from bluetooth import ble 
from bluetooth import 
from bleep import BLEDevice
import bluepy
import datetime

print "Debug"
print "Start scanning devices ..."

while True:
        print datetime.datetime.now()   
        #devices = bluez.discover_devices(duration=2, flush_cache=True, lookup_names=True, device_id=0)
        #devices = ble.discover_devices()
        devices = BLEDevice.discoverDevices()


        for device in devices:
                print device

        print "--------------------------------------------------------------------"

#for address, name in devices.items():
#        print("name: {}, address: {}".format(name, address))