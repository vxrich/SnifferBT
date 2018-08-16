import os

#Comandi necessari a non far crashare il power managment del modulo WiFi e bluetooth

os.system("sudo hciconfig hci0 down")
os.system("sudo hciconfig hci0 up")

print "hci0 sets as up"

from bluetooth import bluez
import datetime

print "-- Test Bluez Module --"
print "Start scanning devices ..."

while True:
        print datetime.datetime.now()   
        devices = bluez.discover_devices(duration=2, flush_cache=True, lookup_names=True, device_id=0)

        for device in devices:
                print device

        print "--------------------------------------------------------------------"

#for address, name in devices.items():
#        print("name: {}, address: {}".format(name, address))