import logging
import nmap
import time
import requests
import threading
from threading import Thread
from mapper import Host

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Enrichment:
    def __init__(self, hosts_class):
        self.hosts_class = hosts_class
        self.scanned_hosts = set()
        self.nm = nmap.PortScanner()
        

    def port_and_vendor_scan(self, ip):
        if ip not in self.scanned_hosts:
            try:
                logger.info(f"Scanning {ip} for open ports...")
                self.nm.scan(ip, arguments='--top-ports 1000', timeout=10)
                self.scanned_hosts.add(ip)
                
                # Cleaning data
                if 'tcp' in self.nm[ip]:
                    port_info = {}
                    lport = list(self.nm[ip]['tcp'].keys())
                    lport.sort()
                    for port in lport:
                        port_info[port] = self.nm[ip]['tcp'][port]['state']
                    print(port_info)
                    
                    # Fetching MAC-IP pair to update the correct host
                    mac = Host.resolve_mac_from_ip(ip)
                    if port_info and mac:
                        host = Host.hosts[mac]
                        if host:
                            host.update_ports(port_info)
                            # Conduct vendor lookup, based on MAC adress
                            thread = threading.Thread(target=self.vendor_enrichment, args=(ip, mac))
                            thread.daemon = True
                            thread.start()
                        else:
                            print(f"No Host instance found for MAC {mac}.")
                    else:
                        print(f"No Host instance found for IP {ip}.")
                else:
                    print(f"No open TCP ports found for {ip}.")
                logger.info(f"Port scan completed for {ip}")
    
            except nmap.PortScannerError as e:
                logger.error(f"port scan failed for {ip}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while scanning {ip}: {e}")
        
    def check_for_new_hosts(self):
        while True:
            for host in self.hosts_class.list_hosts():
                if host.ip not in self.scanned_hosts:
                    self.port_and_vendor_scan(host.ip)
            time.sleep(5)
    
    def start_port_scan(self):
        self.port_thread = Thread(target=self.check_for_new_hosts, daemon=True)
        self.port_thread.start()

    # Runnig extensive Nmap query against selected host
    def nmap_vuln_scan(self, ip):
        logger.info(f"Scanning {ip} with vulners script...")
        self.nm.scan(ip, arguments='-sV --script=vulners')
        vulnerabilities = {}
    
        for host in self.nm.all_hosts():
            host_vulns = {}
    
            for proto in self.nm[host].all_protocols():
                for port in sorted(self.nm[host][proto].keys()):
                    scripts = self.nm[host][proto][port].get('script', {})
                    vulnerabilities_list = []
                    for script_id, script_output in scripts.items():
                        vulnerabilities_list.append(f"Script ID {script_id}, Output: {script_output}")
                        logger.info(f"Port {port}: Script ID {script_id}, Script Output: {script_output}")
                    if vulnerabilities_list:
                        host_vulns[port] = vulnerabilities_list
    
            mac = Host.resolve_mac_from_ip(host)
            if mac in Host.hosts:
                Host.hosts[mac].update_vulners(host_vulns)
            else:
                logger.error(f"No Host found for MAC {mac}")
    
        logger.debug(f"Vulnerabilities collected: {vulnerabilities}")


    def start_vuln_scan(self, ip):
        self.vuln_thread = Thread(target=self.nmap_vuln_scan, args=(ip,), daemon=True)
        self.vuln_thread.start()

    def vendor_enrichment(self, ip, mac):
        url = f"https://api.macvendors.com/{mac}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                vendor = response.text
                print(f'making vendor name update on {ip}')
                Host.create_or_update_host(ip, mac, vendor)
            else:
                vendor = "Unknown"
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve vendor for MAC {mac}: {e}")
            vendor = "Unknown"
    