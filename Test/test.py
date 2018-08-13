from bluetooth import bluez
from bluetooth import ble 
from bluetooth import btcommon

print "Debug"
print "Start scanning devices ..."

try: 
        devices = bluez.discover_devices(duration=2, flush_cache=True, lookup_names=True, device_id=0)
        #devices = ble.discover_devices()
        
except btcommon.BluetoothError as error:
        print "Caught BluetoothError: ", error


for device in devices:
	print device

#for address, name in devices.items():
#        print("name: {}, address: {}".format(name, address))