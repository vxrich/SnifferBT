from bluetooth.ble import BeaconService
import time

service = BeaconService()

service.start_advertising("7270312d-7361-6c6f-7474-6f0000000000",
            1, 1, 1, 200)

time.sleep(25)
service.stop_advertising()

print "Done"