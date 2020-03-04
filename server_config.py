import binascii
HOST_NAME = "localhost"
ID = "root"
PSW = "asusx205ta"
DB_NAME = "devices_db"

rpi_users = [
    ("rpi_1", "192.168.178.37", "password_1"),
    ("rpi_2", "192.168.178.45", "password_2"),
    ("rpi_3", "192.168.178.20", "password_3")
]

CONST_BEACON = [{
        "uuid": binascii.hexlify("rpi_1-angolodx-2.6-2.5"),
        "addr":"B8:27:EB:5B:2C:26",
        "rssi": -69 },
    {
        "uuid": binascii.hexlify("rpi_2-angolosx-0.5-3.3"),
        "addr": "B8:27:EB:B4:1D:1A",
        "rssi": -69
    },
    {
        "uuid": binascii.hexlify("rpi_3-finestra-0.5-0.8"),
        "addr":"B8:27:EB:DA:54:43",
        "rssi": -69
    }]

