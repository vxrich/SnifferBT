from Device import ScanedDevice, RPiBeacon

import binascii
from scipy.spatial.distance import euclidean as dist
from itertools import combinations, groupby, product
from collections import defaultdict
import numpy as np
from numpy.linalg import solve

devices = []
beacons = []

#devices.append(ScanedDevice("rpi_1", "test_1", "BB:BB:BB:BB:BB:BB", -30))
devices.append(ScanedDevice("rpi_1", "test_2", "CC:CC:CC:CC:CC:CC", -50))
devices.append(ScanedDevice("rpi_2", "test_2", "CC:CC:CC:CC:CC:CC", -50))
devices.append(ScanedDevice("rpi_3", "test_2", "CC:CC:CC:CC:CC:CC", -50))
#devices.append(ScanedDevice("rpi_2", "test_3", "DD:DD:DD:DD:DD:DD", -20))
#devices.append(ScanedDevice("rpi_3", "test_1", "BB:BB:BB:BB:BB:BB", -60))

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
points = []
#Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
dev_cp = []
circ = []
for dev in devices: #Per ogni MAC individuato --> dev lista di ScanedDevicec con stesso MAC e diverso rpi_id
    #Viene preso un dispositivo alla volta e confrontato con i RPiBeacon che ho, al corrispondete viene calcolata la 
    #circonferenza con centro RPiBEacon e raggio la distanza alla quale viene trovato il Device
    for d in dev:    
        for b in beacons:
            if d.rpi_id == b.rpi_id:
                dev_cp.append((d,b)) 
                z = b.x**2 + b.y**2 - d.distance**2
                circ.append(np.array([b.x*2,b.y*2,z])) #Ottengo le componenti utili del'eq della circonferenza che corrispondo a ax+by+c 
                print b.rpi_id,b.x*2,b.y*2,z, d.distance

        #Effettuo il prodotto cartesiano tra le circonferenze trovate in modo che nel calcolo delle eq trovo facilemente
        #la retta che congiunge i 2 punti di tangenza tra le circonfereze
        circ_cp = combinations(circ,2) 

        lines = []
        #Calcolo della retta fra due circonferenze sottraendo i termini trovati, corrispondenti agli ultimi 3 termini dell'eq
        #della circonferenza. 
        
        for a,b in circ_cp:
            line = np.subtract(a,b)
            #lin_eq[2]= lin_eq[2]/2
            lines.append(line)
        

# Per trovare l'intersezione utilizzo la funzione di risoluzione dei sistemi lineari
# di numpy, prima pero' devo costruire la matrice A e b
# Le matrici A e b sono riferite a solo 2 rette, perche per costruzione l'intersezione 
# delle altre sare lo stesso punto
print lines

A = np.array([(lines[0])[0:2], (lines[2])[0:2]])
b = np.array([(lines[0])[2],(lines[2])[2]])
# points conterre' elementi del tipo np.array

points.append(np.linalg.solve(A,b))

print points