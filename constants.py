TAG = ["name", "dev_found:", "rssi"]

WAITING_TIME = 120 #Secondi
SCAN_TIME = 10 #Secondi 
SLEEP_BETWEEN_SCAN = 300
SCAN_LOOP = 1

# Trovi questi parametri https://github.com/IanHarvey/bluepy/blob/master/bluepy/btle.py
COMPLETE_NAME = 0X09 #ID nome nell'oggetto ScanEntry
PUBLIC_TARGET_ADDRESS = 0X17
RANDOM_TARGET_ADDRESS = 0x18
MANUFACTURER = 0xFF

IS_BLE = 1
NOT_BLE = 0

ADV_DATA = ""
ADV_TIME = 15

DASH_POS = [8, 13, 18, 23]
BEACON_SCAN_TIME = 15
