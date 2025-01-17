import os
import nmap
import psutil
import struct
import socket
import logging
import ipaddress
from scapy.all import sniff, Ether, ARP, IP
from threading import Thread

import logging

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Host:
    hosts = {}
    _observers =[]

    def __init__(self, ip, mac, vendor='Unknown'):
        self.ip = ip
        if mac =='UNKNOWN':
            ip_octets = ip.split('.')
            uniqueID = f"{ip_octets[-2]}.{ip_octets[-1]}"
            self.mac = f"UNKNOWN.{uniqueID}"
        else:
            self.mac = mac.upper()
        self.vendor = vendor
        self.ports = {}
        self.vulners = {}
        self.auth_info = []
        Host.hosts[self.mac] = self

    @staticmethod
    def create_or_update_host(ip, mac, vendor='Unknown'):
        if mac =='UNKNOWN':
            ip_octets = ip.split('.')
            uniqueID = f"{ip_octets[-2]}.{ip_octets[-1]}"
            mac = f"UNKNOWN.{uniqueID}"
        else:
            mac = mac.upper()

        existing_host = Host.hosts.get(mac)
        if existing_host:
            if existing_host.ip != ip:
                logger.info(f"Updating host {ip} with MAC address: {mac}")
            existing_host.mac = mac
            existing_host.vendor = vendor
        else:
            Host(ip, mac, vendor)
        Host.notify_observers()

    def update_ports(self, port_info):
        for port, details in port_info.items():
            self.ports[port] = details
        Host.notify_observers()

    def update_vulners(self, vuln_info):
        self.vulners.update(vuln_info)
        Host.notify_observers()

    @classmethod
    def update_auth_info(cls, ip, auth_info):
        mac = cls.resolve_mac_from_ip(ip)
        if mac and mac in cls.hosts:
            cls.hosts[mac].auth_info.append(auth_info)
            cls.notify_observers()

    @classmethod
    def list_hosts(cls):
        return list(cls.hosts.values())

    @staticmethod
    def resolve_mac_from_ip (ip):
        for mac, host in Host.hosts.items():
            if host.ip == ip:
                return mac
        return None

    def attributes_as_list(self):
        return [self.ip, self.mac, self.vendor, self.ports]

    @classmethod
    def register_observer(cls, callback):
        cls._observers.append(callback)

    @classmethod
    def notify_observers(cls):
        host_list = cls.list_hosts()
        for callback in cls._observers:
            callback(host_list)


class NetworkMapper:
    def __init__(self):
        self.interface, self.subnet = self.get_network_interfaces_and_subnet()
        if self.subnet:
            subnet = ipaddress.ip_network(self.subnet, strict=False)
            self.netw = int(subnet.network_address)
            self.mask = int(subnet.netmask)
        else:
            self.netw = None
            self.mask = None

    @staticmethod
    def get_network_interfaces_and_subnet():
        interfaces_info = psutil.net_if_addrs()
        for interface_name, interface_addresses in interfaces_info.items():
            for address in interface_addresses:
                if address.family == 2 and address.netmask is not None:  
                    ip_address = address.address
                    if ip_address.startswith("127.") or \
                        ip_address.startswith("169.254."):
                        continue
                    netmask = address.netmask
                    cidr = sum(bin(int(x)).count('1') for x in \
                        netmask.split('.'))
                    subnet = f"{ip_address}/{cidr}"
                    return interface_name, subnet
        return None, None
    
    def nmap_arp_scan(self):
        if self.subnet:
            nm = nmap.PortScanner()
            logger.info(f"Performing ARP scan on {self.subnet}...")
            nm.scan(hosts=self.subnet, arguments='-sn -PR')
            for host in nm.all_hosts():
                ip = nm[host]['addresses'].get('ipv4', '')
                mac = nm[host]['addresses'].get('mac', 'Unknown')
                vendor = nm[host].get('vendor', {}).get(mac, 'Unknown')
                Host.create_or_update_host(ip, mac, vendor)
            logger.info(f"Found {len(Host.hosts)} live hosts.")
        else:
            logger.error("No valid subnet found for ARP scanning.")
    
    def packet_sniffing(self):
        if os.geteuid() != 0:
            logger.error(
                "Packet inspection requires root privileges. Skipping...")
            return
        try:
            sniff(prn=self.packet_handler, filter="", store=False, \
                iface=self.interface)
        except Exception as e:
            logger.error("Error during packet sniffing: {}".format(e))
    
    def packet_handler(self,packet):
        if Ether in packet:
            mac_address = packet[Ether].src.upper()
            ip_address = None
            if IP in packet:
                ip_address = packet[IP].src
            elif ARP in packet:
                ip_address = packet[ARP].psrc
    
            # Ignore IP's outside the local network.
            if ip_address:
                try:
                    ip_int = int(ipaddress.ip_address(ip_address))
                    if (ip_int & self.mask) != self.netw:
                        return  
                except ValueError as e:
                    logger.error(f"Invalid IP address {ip_address}: {e}")
                    return
    
    def start_monitoring(self):
        self.nmap_arp_scan()
        self.sniffer_thread = Thread(target=self.packet_sniffing, daemon=True)
        self.sniffer_thread.start()
