import datetime
import os
import MySQLdb

# C'è da creare un user mysql prima di avviare il programma oppure lo si crea direttamente
# da qui dentro connettendosi da root
HOST_NAME = "localhost"
ID = "server"
PSW = ""
DB_NAME = "devices_db"

rpi_users = [
    ("rpi_1", "192.168.1.2", "password_1"),
    ("rpi_2", "192.168.1.3", "password_2")
]

CREATE_DB = "CREATE DATABASE IF NOT EXISTS devices_db"
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS devices (rpi_id varchar(10), name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(12))"


db.MySQLDdb.connect(HOST_NAME, ID, PSW, DB_NAME)
cur = db.cursor()

db.execue(CREATE_DB)
db.execute(CREATE_TABLE)

for user in rpi_users:
    db.execute("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFED BY '%s'" % (user[0], user[1], user[2]))

db.commit()