from bluetooth.ble import DiscoveryService
import datetime

print "-- Test Bluez BLE --"
print "Start scanning devices ..."

service = DiscoveryService()

while True:
        print datetime.datetime.now()   
        devices = service.discover(2)	

        for address, name in devices.items():
    		print("name: {}, address: {}".format(name, address))

        print "--------------------------------------------------------------------"

	for dev in devices:
		print dev








