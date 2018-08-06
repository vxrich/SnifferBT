import bluetooth

print "looking for nearby devices..."
deviceDiscoverer = bluetooth.DeviceDiscoverer()
deviceDiscoverer.find_devices(duration=30)
devices = deviceDiscoverer.device_discovered()
print devices