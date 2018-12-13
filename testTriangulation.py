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

#I devices sono raggruppati per addr, quindi dev e' una lista
for dev in devices:
    if len(dev) < 3:
        print "Device %s is not found by all the RPi Beacon"
    else:
        points = []
        #Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
        dev_cp = []
        
        for d in dev:
            vects = [] #Conterra' i dati di ogni circonferenza per un dato dispositivo
            vects_cp=[]
            for b in beacons:
                if d.rpi_id == b.rpi_id:
                    dev_cp.append((d,b)) 
                    tn = b.x**2 + b.y**2 - d.distance**2 #Rappresenta il termine noto dell'equazione della circonferenza
                    vects.append(np.array([b.x,b.y,tn])) # Calcolo solo la terza riga della matice perche' le altre non sevono

            vects_cp = combinations(vects,2)
            lin_eqs = []
        
            for a,b in vects_cp:
                lin_eq = np.subtract(a,b)
                #lin_eq[2]= lin_eq[2]/2
                lin_eqs.append(lin_eq)

            A = np.array([(lin_eqs[0])[0:2], (lin_eqs[1])[0:2]])
            b = np.array([(lin_eqs[0])[2],(lin_eqs[1])[2])
            
            points.append(np.solve(A,b))