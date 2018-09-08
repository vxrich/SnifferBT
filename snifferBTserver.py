#coding=utf-8
"""
Sniffer Bluetooth server, crea il DB e gli users, 

Dati Database:
Name = devices_db
Table = devices(rpi_id, name, addr, rssi, date, time, is_ble)

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
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS devices (rpi_id varchar(10), name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(12), is_ble tinyint(1))"
GRANT = "GRANT PREVILEGES ON *.* TO '%s'"

os.system("sudo service mysql restart")
db = MySQLdb.connect(HOST_NAME, ID, PSW)
cur = db.cursor()

cur.execute(CREATE_DB)
cur.execute(USE_DB)
cur.execute(CREATE_TABLE)

for user in rpi_users:
    cur.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))
    cur.execute("GRANT ALL PRIVILEGES ON *.* TO '%s'@'%s' IDENTIFIED BY '%s'" % (user[0], user[1], user[2]))

cur.execute("FLUSH PRIVILEGES;")

while True:

    print "--------------------------"

    cur.execute("SELECT * FROM devices")
    rows = cur.fetchall()

    for row in rows:
        print row

    time.sleep(30)
db.commit()