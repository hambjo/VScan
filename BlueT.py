import asyncio
from bleak import BleakScanner
from mapper import Host
import logging

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BluetoothScanner:
    def __init__(self):
        self.devices = {}

    async def discover_devices(self, scan_duration=10):
        def detection_callback(device, adv_data):
            mac_address = device.address.upper()
            self.devices[mac_address] = {
                "name": adv_data.local_name or device.name or "Unknown",
                "rssi": adv_data.rssi
            }

        async with BleakScanner(detection_callback) as scanner:
            await asyncio.sleep(scan_duration)
        
        return self.devices

    async def start_scan(self):
        devices = await self.discover_devices()
        self.update_hosts_with_bluetooth(devices)

        if devices:
            print("Scanned Bluetooth Devices:")
            for address, info in devices.items():
                print(f"Device {info['name']} at {address} - RSSI: {info['rssi']}")
        else:
            print("No Bluetooth devices found.")
        print(f"Final scanned devices: {self.devices}")

    def start_thread(self):
        asyncio.run(self.start_scan())
 
    def update_hosts_with_bluetooth(self, devices):
        for uuid, info in devices.items():  # uuid is the key, info is the nested dict with 'name' and 'rssi'
            ip = "Bluetooth"  # Placeholder IP for Bluetooth devices
            vendor = "Unknown"  # Placeholder for vendor info
    
            # Check if the UUID is already in the hosts dictionary
            if uuid in Host.hosts:
                host = Host.hosts[uuid]
                logger.info(f"Updating existing host {uuid} with new information.")
            else:
                # Create a new Host instance if it doesn't exist
                host = Host(ip, uuid, vendor)
                logger.info(f"Creating new host for {uuid}.")
    
            # Update the host name with the Bluetooth device's name
            host.name = info['name']
    
            # Store other relevant information if needed (e.g., RSSI)
            # If you need to store RSSI or other specific data, you might need to add attributes to the Host class
            # Example: host.rssi = info['rssi']