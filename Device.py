import datetime
import binascii

"""
Classe che crea un oggetto device scansionato con tutti gli attributi necessari alla creazione
di un record nel database 
"""
class ScanedDevice:
    
    def __init__(self,rpi_id, name, addr, rssi, x = None, y = None):
        self.rpi_id = rpi_id
        self.name = name
        self.addr = addr
        self.distance = self._rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))
        self.services = []
        self.x = x
        self.y = y

    def _rssiToMeters(self, rssi):
    
        #RSSI = TxPower - 10 * n * lg(d)
        #n = 2 (in free space)
        
        #d = 10 ^ ((TxPower - RSSI) / (10 * n))
        N = 2
        txPower = -64
        return round(pow(10, (txPower - rssi) / (10 * N)),2)


    def setServices(self, services):
        self.services = services

    def setPosition(self, x,y):
        self.x = x
        self.y = y
    

    def printData(self):
        print "%s - %s - %d at %s - %s " % (self.name, self.addr, self.distance, self.date, self.time)
        for s in self.services:
            print s
        print "-----------------------------------------------"

"""
Classe che crea un oggetto Beacon, in particolare un altro RPi che effettua la scansione 
in un'altra parte dell'ambiente
"""
class RPiBeacon:

    def __init__(self, data, addr, rssi):
        self.rpi_id, self.location, self.x, self.y = self._extractData(data)
        self.addr = addr
        self.distance = self._rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))

    def setPosition(self, x,y):
        self.x = x
        self.y = y

    def _extractData(self, data):

        for ch in ['-', "00"]:
            data = data.replace(ch, '')

        convStr = binascii.unhexlify(data)
        splitData = convStr.split('-')

        return splitData[0], splitData[1], splitData[2], splitData[3]

    def _rssiToMeters(self, rssi):
    
        #RSSI = TxPower - 10 * n * lg(d)
        #n = 2 (in free space)
     
        #d = 10 ^ ((TxPower - RSSI) / (10 * n))
        N = 2
        txPower = -64
        return round(pow(10, (txPower - rssi) / (10 * N)),2)


    def printData():
        print "%d - %s" % (self.rpi_id, self.location)
        print "-----------------------------------------------"
    