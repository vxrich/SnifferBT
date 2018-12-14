from Device import ScanedDevice, RPiBeacon

import binascii
from scipy.spatial.distance import euclidean as dist
from itertools import combinations, groupby, product
from collections import defaultdict
import numpy as np
from numpy.linalg import solve

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
points = []
#Prodotto cartesiano dei Beacon che hanno trovato il dispositivo
dev_cp = []
vects = []
for dev in devices: 
    for d in dev:
        for b in beacons:
            if d.rpi_id == b.rpi_id:
                dev_cp.append((d,b)) 
                z = b.x**2 + b.y**2 - d.distance**2
                vects.append(np.array([b.x*2,b.y*2,z])) # Calcolo solo la terza riga della matice perche' le altre non sevono
                print vects

        vects_cp = combinations(vects,2)
        lin_eqs = []
        """
        Prendo le combianzioni lineari delle matrici delle circonferenze e le sottraggo 
        per ottenere le rette secanti i 2 punti di intersezione tra le coppie di circonferenze
        con la matrice delle rette trovero' il punto di intersezione di quest'ultime.
        Questo metodo mi permette di trovare un punto anche con misurazioni imprecise
        In questo modo e' possibile intersecare anche solo 2 rette e si trova il punto 

        Necessario implementare controllo sulla lunghezza dei raggi nel caso 2 circonferenze non si
        toccano
        """
        for a,b in vects_cp:
            lin_eq = np.subtract(a,b)
            #lin_eq[2]= lin_eq[2]/2
            lin_eqs.append(lin_eq)

        # Per trovare l'intersezione utilizzo la funzione di risoluzione dei sistemi lineari
        # di numpy, prima pero' devo costruire la matrice A e b
        # Le matrici A e b sono riferite a solo 2 rette, perche per costruzione l'intersezione 
        # delle altre sare lo stesso punto
        print lin_eqs
        A = np.array([(lin_eqs[0])[0:2], (lin_eqs[1])[2]])
        b = np.array([(lin_eqs[0])[2],(lin_eqs[1])[2]])
        # points conterre' elementi del tipo np.array
        points.append(np.solve(A,b))

    print points