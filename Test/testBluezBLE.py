from bluetooth import ble 
import datetime

print "-- Test Bluez BLE --"
print "Start scanning devices ..."

while True:
        print datetime.datetime.now()   
        
        devices = ble.discover_devices()

        for device in devices:
                print device

        print "--------------------------------------------------------------------"

#for address, name in devices.items():
#        print("name: {}, address: {}".format(name, address))