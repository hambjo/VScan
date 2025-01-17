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
            mac_address = device.address
            self.devices[mac_address] = {
                "name": adv_data.local_name or device.name or "Unknown"
            }

        async with BleakScanner(detection_callback) as scanner:
            await asyncio.sleep(scan_duration)
        
        return self.devices

    def start_thread(self):
        asyncio.run(self.discover_devices())
        self.update_hosts_with_bluetooth(self.devices)
 
    def update_hosts_with_bluetooth(self, devices):
        for uuid, info in devices.items():
            ip = "Bluetooth"
            vendor = info['name'] or "Unknown"
    
            if uuid in Host.hosts:
                host = Host.hosts[uuid]
                logger.info(
                    f"Updating existing host {uuid} with new information."
                )
            else:
                host = Host(ip, uuid, vendor)
            
            host.name = info['name']
            host.vendor = vendor
            Host.notify_observers()
        
        logger.info(f"CFound {len(devices)} Bluetooth devices.")
