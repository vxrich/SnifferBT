from bluetooth import bluez
from bluetooth import ble 

print "Start scanning devices ..."

devices = bluez.discover_devices(duration=8, flush_cache=True, lookup_names=True)
#devices = ble.discover_devices()

for device in devices:
	print device

for address, name in devices.items():
        print("name: {}, address: {}".format(name, address))