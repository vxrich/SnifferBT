from bluepy.btle import Scanner, DefaultDelegate
import datetime

"""
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print "Discovered device", dev.addr
        elif isNewData:
            print "Received new data from", dev.addr

scanner = Scanner().withDelegate(ScanDelegate())
"""

COMPLETE_NAME = 0X09
PUBLIC_TARGET_ADDRESS = 0x17

date = datetime.date
time = datetime.time


scanner = Scanner()

devices = scanner.scan(10)

clean_dev = [[dev.getValueText(COMPLETE_NAME), dev.addr, dev.rssi] for dev in devices]

for dev in clean_dev:
    print dev

"""
for dev in devices:
    print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
    for (adtype, desc, value) in dev.getScanData():
        print "  %s = %s" % (desc, value)
"""