import tkinter as tk
import logging
from tkinter import ttk
from itertools import cycle
from mapper import Host, NetworkMapper
from http_auth import AuthAttacker
from enrichment import Enrichment
from jamming import Jammer
from BlueT import BluetoothScanner
from ftp_anon import FtpAnon

DARK_BG = "#383838"
DARK_TEXT = "#ffffff"
DARK_SECONDARY = "#404040"
DARK_HIGHLIGHT = "#5294e2"

logging.basicConfig(level=logging.INFO, \
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScannerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("IoT Device Scanner")
        self.mapper = NetworkMapper()
        self.enrichment = Enrichment()
        self.auth_attacker = AuthAttacker()
        self.bluetooth = BluetoothScanner()
        self.ftp_anon = FtpAnon()
        self.details_windows = {}
        self.port_labels = {}
        self.vuln_labels = {}
        self.auth_labels = {}
        self.ftp_labels = {}
        
        Host.register_observer(self.update_host_info)
        Host.register_observer(self.update_tree_view)
        self.set_dark_theme()
        self.init_gui()
        self.status_label = tk.Label(self.master, text="Application is \
            currently silently looking for devices on your network...",\
            bg=DARK_BG, fg=DARK_TEXT)

    def set_dark_theme(self):
        self.master.configure(bg=DARK_BG)
        style = ttk.Style()
        style.theme_use('alt')
        style.configure('Treeview', background=DARK_SECONDARY, \
            foreground=DARK_TEXT, fieldbackground=DARK_BG)
        style.map('Treeview', background=[('selected', DARK_HIGHLIGHT)], \
            foreground=[('selected', DARK_BG)])
        style.configure('TLabel', background=DARK_BG, foreground=DARK_TEXT)
        style.configure('TButton', background=DARK_SECONDARY, \
            foreground=DARK_TEXT)
        style.map('TButton', background=[('active', DARK_HIGHLIGHT)], \
            foreground=[('active', DARK_TEXT)])

    def init_gui(self):
        self.init_start_menu()
        self.init_treeview()

    def init_start_menu(self):
        self.welcome_label = tk.Label(self.master, text="Welcome to this IoT "
            "Vulnerability Scanner. Please click 'Start scan' to begin.")
        self.welcome_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.start_scan_button = tk.Button(self.master, \
            text="Start scan", command=self.start_scan)
        self.start_scan_button.pack(pady=20)

    def init_treeview(self):
        self.tree = ttk.Treeview(self.master, columns=("IP Address", \
            "MAC Address", "Vendor"), show="headings")
        self.tree.heading("IP Address", text="IP Address")
        self.tree.heading("MAC Address", text="MAC Address")
        self.tree.heading("Vendor", text="Vendor")
        self.tree.bind('<<TreeviewSelect>>', self.on_host_select)
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def start_scan(self):
        self.mapper.start_monitoring()
        self.enrichment.start_port_scan()
        self.bluetooth.start_thread()
        self.welcome_label.pack_forget()
        self.start_scan_button.pack_forget()
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_host_select)

    def update_tree_view(self, host_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
        for host in host_list:
            host_values = host.attributes_as_list()
            self.tree.insert("", "end", values=host_values)

    def update_host_info(self, host_list):
        for host in host_list:
            if host.mac in self.details_windows:
                self.update_details_window(host)

    def on_host_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected_item = self.tree.selection()[0]
        selected_host_mac = self.tree.item(selected_item, 'values')[1]
        selected_host = Host.hosts.get(selected_host_mac)
        if selected_host:
            self.show_host_details(selected_host)

    def show_host_details(self, host):
        if host.mac in self.details_windows and \
            self.details_windows[host.mac].winfo_exists():
            self.details_windows[host.mac].lift()
        else:
            self.create_device_window(host)
        self.update_details_window(host)

    def create_device_window(self, host):
        details_window = tk.Toplevel(self.master)
        details_window.title(f"Details for {host.ip} - {host.mac}")
        self.details_windows[host.mac] = details_window

        tk.Label(details_window, text="Open ports:").grid\
            (row=0, column=0, sticky='w')
        tk.Label(details_window, text="Vulnerabilities:").grid\
            (row=1, column=0, sticky='w')
        tk.Label(details_window, text="Authentication:").grid\
            (row=2, column=0, sticky='w')

        ports_label = tk.Label(details_window, text="")
        ports_label.grid(row=0, column=1, sticky='w')
        vulns_label = tk.Label(details_window, text="")
        vulns_label.grid(row=1, column=1, sticky='w')
        auth_label = tk.Label(details_window, text="")
        auth_label.grid(row=2, column=1, sticky='w')

        # Action Buttons
        test_vuln_button = tk.Button(details_window, text="Test for CVSS's",
            command=lambda: self.enrichment.start_vuln_scan(host.ip))
        test_vuln_button.grid(row=0, column=2)
        dos_attack_button = tk.Button(details_window, text="DoS Attack",
            command=lambda: self.open_dos_window(host))
        dos_attack_button.grid(row=1, column=2)
        auth_attack_button = tk.Button(details_window, text=\
            "HTTP Attack",
            command=lambda: self.auth_attacker.start_attack(host.ip, \
                list(host.ports.keys())))
        auth_attack_button.grid(row=2, column=2)
        ftp_attack_button = tk.Button(details_window, text="FTP Attack",
            command=lambda: self.ftp_anon.start_attack(host.ip))
        ftp_attack_button.grid(row=3, column=2)


        for i in range(3):
            details_window.grid_columnconfigure(i, weight=1)

        self.port_labels[host.mac] = ports_label
        self.vuln_labels[host.mac] = vulns_label
        self.auth_labels[host.mac] = auth_label

    def update_details_window(self, host):
        def safe_update():
            vulns_text = str(host.vulners) if host.vulners else "None"
            ports_text = ", ".join(str(port) for port in host.ports) if \
                host.ports else "None"
            auth_text = "\n".join(host.auth_info) if host.auth_info else "None"

            if self.port_labels[host.mac].winfo_exists():
                self.port_labels[host.mac].config(text=ports_text, \
                    wraplength=700)
            if self.vuln_labels[host.mac].winfo_exists():
                self.vuln_labels[host.mac].config(text=vulns_text, \
                    wraplength=700, anchor='w', justify='left')
            if self.auth_labels[host.mac].winfo_exists():
                self.auth_labels[host.mac].config(text=auth_text, \
                    wraplength=700, anchor='w', justify='left')
    
        self.master.after(0, safe_update)

    def open_dos_window(self, host):
        attack_window = tk.Toplevel(self.master)
        attack_window.title("DoS Attack Control")
        self.setup_dos_window(attack_window, host)

    def setup_dos_window(self, window, host):
        warning_label = tk.Label(window, text="Warning: This is an intrusive"
            " test.Only run it for short periods and with care.", fg="red")
        warning_label.pack(pady=10)
        window.jammer = Jammer(host)
        
        start_button = tk.Button(window, text="Start Attack", command=lambda: \
            self.start_dos_attack(window, host))
        start_button.pack(pady=10)
        window.start_button = start_button
        
        stop_button = tk.Button(window, text="Stop Attack", command=lambda: \
            self.stop_dos_attack(window))
        stop_button.pack(pady=10)
    
        window.attack_message_label = tk.Label(window, \
            font=("Helvetica", 12), wraplength=400)
        window.attack_message_label.pack_forget()
        window.protocol("WM_DELETE_WINDOW", lambda: self.stop_dos_attack\
            (window, close=True))
    
    def start_dos_attack(self, window, host):
        window.jammer.start_attack()
        window.start_button.pack_forget()
        message_text = (f"{host.vendor} with IP {host.ip} is currently "
            "being flooded with data. If you can't connect with it now,"
            " it is prone to DoS attacks. Remember to stop this attack "
            "as soon as you're through with testing")
        window.attack_message_label.config(text=message_text)
        window.attack_message_label.pack(pady=10)

    def stop_dos_attack(self, window, close=False):
        if hasattr(window, 'jammer'):
            window.jammer.stop_attack()
        window.attack_message_label.pack_forget()
        if close:
            window.destroy()
        else:
            window.destroy()

    
