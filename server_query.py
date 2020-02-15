CREATE_DB = "CREATE DATABASE IF NOT EXISTS devices_db"
USE_DB = "USE devices_db"

CREATE_TABLE_SERIALIZE_DEVICE = "CREATE TABLE IF NOT EXISTS serial_device (device_obj varchar(500))"
CREATE_TABLE_SERIALIZE_BEACON = "CREATE TABLE IF NOT EXISTS serial_beacon (beacon_obj varchar(500))"
CREATE_TABLE_DEVICE = "CREATE TABLE IF NOT EXISTS device (rpi_id varchar(10), name varchar(20), addr varchar(17), rssi int(4), date varchar(12), time varchar(8), PRIMARY KEY(rpi_id, addr))"
CREATE_TABLE_BEACON = "CREATE TABLE IF NOT EXISTS rpi_beacon (id varchar(10) PRIMARY KEY, location varchar(15), addr varchar(17), rssi int(4), date varchar(12), time varchar(8));"

fromGRANT = "GRANT PREVILEGES ON *.* TO '%s'"

FLUSH = "FLUSH PRIVILEGES;"

SELECT_ALL_DEV = "SELECT * FROM devices"
SELECT_ALL_SER_DEV = "SELECT * FROM serial_devices"

queries = [CREATE_DB, USE_DB, CREATE_TABLE_BEACON, CREATE_TABLE_DEVICE, CREATE_TABLE_SERIALIZE_DEVICE, CREATE_TABLE_SERIALIZE_BEACON]