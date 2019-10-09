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
        #La distanza alla quale viene localizzato dal dispositivo specificati con rpi_id
        self.distance = self._rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))
        self.services = []
        self.type = None
        self.x = x
        self.y = y
        self.position = (x,y)

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
        self.position = (x,y)

    def printData(self):
        if self.x == None and self.y == None:
            print "Scaned by %s at %.2fm --> %s - %s at %s - %s " % (self.rpi_id, self.distance, self.name, self.addr,  self.date, self.time)
        else: 
            print "Scaned by %s at %.2fm --> %s - %s - [%.2f, %.2f] at %s - %s " % (self.rpi_id, self.distance, self.name, self.addr, self.x, self.y, self.date, self.time)
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
        # Distanza alla quale viene indentificato, irrilevante se inseriamo le coordinate esatte di dove 
        # verra posizionato
        self.distance = self._rssiToMeters(rssi)
        self.date = str(datetime.datetime.now().date())
        self.time = str(datetime.datetime.now().time().replace(microsecond=0))
        # Il centro del cerchio per la localizzazione del dispositivo viene abbinata alla ScanedDevice.distance
        self.position = (self.x, self.y)

    def setPosition(self, x,y):
        self.x = x
        self.y = y

    def _extractData(self, data):

        for ch in ['-', "00"]:
            data = data.replace(ch, '')

        convStr = binascii.unhexlify(data)
        splitData = convStr.split('-')

        id, location, x ,y = "", "", None, None

        try:
            id, location, x, y = splitData[0], splitData[1], splitData[2], splitData[3]
        except IndexError:
            print "UUID missing parts!"

        return id, location, int(x), int(y)

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
    