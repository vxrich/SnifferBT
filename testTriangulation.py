from Device import ScanedDevice, RPiBeacon

import binascii
from scipy.spatial.distance import euclidean as dist
from itertools import combinations, groupby, product
from collections import defaultdict

devices = []
beacons = []

devices.append(ScanedDevice("rpi_1", "test_1", "BB:BB:BB:BB:BB:BB", -30))
devices.append(ScanedDevice("rpi_1", "test_2", "CC:CC:CC:CC:CC:CC", -36))
devices.append(ScanedDevice("rpi_2", "test_2", "CC:CC:CC:CC:CC:CC", -50))
devices.append(ScanedDevice("rpi_3", "test_2", "CC:CC:CC:CC:CC:CC", -87))
devices.append(ScanedDevice("rpi_2", "test_3", "DD:DD:DD:DD:DD:DD", -20))
devices.append(ScanedDevice("rpi_3", "test_1", "BB:BB:BB:BB:BB:BB", -60))

beacons.append(RPiBeacon(binascii.hexlify("rpi_1-angolodx-0-0"),"11:11:11:11:11:11",-50))
beacons.append(RPiBeacon(binascii.hexlify("rpi_2-angolosx-10-10"),"22:22:22:22:22:22",-32))
beacons.append(RPiBeacon(binascii.hexlify("rpi_3-finestra-0-10"),"33:33:33:33:33:33",-67))

#Raggruppo i dispositivi per MAC address
groups = defaultdict(list)
for dev in devices:
    groups[dev.addr].append(dev)
devices = groups.values()

cart_product = []

print devices

for dev in devices:
    cp = []
    for d in dev:
        print d.addr
        for b in beacons:
            if d.rpi_id == b.rpi_id:
                cp.append((b.position, d.distance))
    cart_product.append(cp)

for cp in cart_product:
    print cp