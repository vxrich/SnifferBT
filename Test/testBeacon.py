from bluetooth.ble import BeaconService
import time

service = BeaconService()

service.start_advertising("aaaaaaaa-2222-3333-4444-555555555554",
            1, 1, 1, 200)

time.sleep(25)
service.stop_advertising()

print "Done"