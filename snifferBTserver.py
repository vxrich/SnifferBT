import datetime
import os
import MySQLDB

HOST_NAME = ""
ID = ""
PSW = ""
DB_NAME = ""

CREATE_DB = "CREATE DATABASE IF NOT EXISTS devices_db"
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS devices (name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(12)"

db.MySQLDB.connect(HOST_NAME, ID, PSW, DB_NAME)
cur = db.cursor()

db.execue(CREATE_DB)
db.execute(CREATE_TABLE)

db.commit()