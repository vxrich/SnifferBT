import datetime

"""
Classe che crea un oggetto device scansionato con tutti gli attributi necessari alla creazione
di un record nel database 
"""
class ScanedDevice:
    
    def __init__(self,rpi_id, name, addr, rssi):
        self.rpi_id = rpi_id
        self.name = name
        self.addr = addr
        self.distance = self._rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))
        self.services = []

    def _rssiToMeters(self, rssi):
    
    #RSSI = TxPower - 10 * n * lg(d)
    #n = 2 (in free space)
     
    #d = 10 ^ ((TxPower - RSSI) / (10 * n))
        txPower = -50
        return round(pow(10, (txPower - rssi) / (10 * 2)),2)


    def setServices(self, services):
        self.services = services

    

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
        self.id, self.location = self._extractData(data)
        self.addr = addr
        self.distance = _rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))

    def printData():
        print "%d - %s" % (self.id, self.location)
        print "-----------------------------------------------"

    def _extractData(data):

        for ch in ['-', "00"]:
            data = data.replace(ch, '')

        convStr = binascii.unhexlify(data)
        splitData = convStr.split('-')

        return splitData[0], splitData[1]

    def _rssiToMeters(rssi):
    
        #RSSI = TxPower - 10 * n * lg(d)
        #n = 2 (in free space)
     
        #d = 10 ^ ((TxPower - RSSI) / (10 * n))

        return round(pow(10, (txPower - rssi) / (10 * 2)),2)