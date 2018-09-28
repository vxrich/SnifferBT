#coding=utf-8
"""
Sniffer Bluetooth server, crea il DB e gli users, 

Dati Database:
Name = devices_db
Table = devices(rpi_id, name, addr, rssi, date, time)

Se all'avvio appare l'errore 2002 
sudo service mysql restart

In un nuovo ambiente è necessario creare gli USERS per loggarsi in mysql:
CREATE USER 'nome'@'localhost' IDENTIFIED BY 'nome';
GRANT ALL PRIVILEGES ON *.* TO 'nome'@'localhost';
"""

import datetime
import os
import MySQLdb
import time
import warnings
from __future__ import division

#Permette di catturare nei try/except i warnings come se fossero errori in modo
# da gestirli meglio
warnings.filterwarnings('error', category=MySQLdb.Warning)

# C'è da creare un user mysql prima di avviare il programma oppure lo si crea direttamente
# da qui dentro connettendosi da root
HOST_NAME = "localhost"
ID = "root"
PSW = "asusx205ta"
DB_NAME = "devices_db"

rpi_users = [
    ("rpi_1", "192.168.1.1", "password_1"),
    ("rpi_2", "192.168.1.3", "password_2"),
    ("rpi_3", "192.168.1.15", "password_1")
]

CREATE_DB = "CREATE DATABASE IF NOT EXISTS devices_db"
USE_DB = "USE devices_db"
CREATE_TABLE_DEVICE = "CREATE TABLE IF NOT EXISTS devices (rpi_id varchar(10), name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(8), PRIMARY KEY(rpi_id, addr))"
CREATE_TABLE_BEACON = "CREATE TABLE IF NOT EXISTS rpi_beacons (id varchar(10) PRIMARY KEY, location varchar(15), addr varchar(17), rssi int(4), date varchar(12), time varchar(8));"
GRANT = "GRANT PREVILEGES ON *.* TO '%s'"

def dbStartUp():

    try:
        db = MySQLdb.connect(HOST_NAME, ID, PSW)
        cur = db.cursor()

        cur.execute(CREATE_DB)
        cur.execute(USE_DB)
        cur.execute(CREATE_TABLE_DEVICE)
        cur.execute(CREATE_TABLE_BEACON)
    except MySQLdb.Warning:
        print "Database is already working!"


    for user in rpi_users:
        try:
            cur.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))
        except MySQLdb.Warning:
            print "User %s is already created!" % (user[0])    
        cur.execute("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))
    
    cur.execute("FLUSH PRIVILEGES;")

    db.commit()
    db.close()

def printData():
    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()
    
    cur.execute(USE_DB)

    print "--------------------------"
    
    cur.execute("SELECT * FROM devices")
    rows = cur.fetchall()

    for row in rows:
        print row

    db.commit()
    db.close()

def rssiToMeters(rssi):
    
    #RSSI = TxPower - 10 * n * lg(d)
    #n = 2 (in free space)
     
    #d = 10 ^ ((TxPower - RSSI) / (10 * n))

 
    return round(pow(10, (txPower - rssi) / (10 * 2)),2)

#Metodo che permette di stimare le persone nell'area scansionata
def evaluationData():

    db = MySQLdb.connect(HOST_NAME, ID, PSW)
    cur = db.cursor()
    
    cur.execute(USE_DB)

    n_dev = cur.execute("SELECT COUNT(*) FROM devices GROUP BY addr;")
    print n_dev


os.system("sudo service mysql restart")

dbStartUp()

while True:

    printData()
    evaluationData()
    time.sleep(30)