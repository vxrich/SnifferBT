#Appende i dispositivi trovati nella lista devices
def scan_devices():

    devices = []

    print "Start scanning devices ..."
    os.system("sudo hciconfig hci0 down")
    os.system("sudo hciconfig hci0 up")
    
    scandevices = bluez.discover_devices(duration=SCAN_TIME, flush_cache=True, lookup_names=True, device_id=0)

    for scandevice in scandevices:
        for name, addr in scandevice.items():
            devices.append(ScanedDevice(name, addr, None, NOT_BLE))

    print "Scan completed!"
    print "-----------------------------------------------"

    return devices 

#Appende i dispositivi BLE trovati nella lista devices
def lescan_devices():

    devices = []
    print "Start scanning LE devices ..."

    lescanner = Scanner()
    
    #Lista di oggetti bluepy.btle.ScanEntry
    ledevices = lescanner.scan(SCAN_TIME)

    #clean_dev = [[dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi] for dev in ledevices]
    #devices.append( ScanedDevice(dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi, IS_BLE) for dev in ledevices )

    for ledev in ledevices:
        devices.append(ScanedDevice(ledev.getValueText(COMPLETE_NAME), ledev.addr, ledev.rssi, IS_BLE))

    print "Scan completed!"
    print "-----------------------------------------------"

    return devices