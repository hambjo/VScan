# VScan, an IoT Vulnerability Scanner
This repository includes Python files that try to detect vulnerabilities in devices at your home network. (the computer deploying this must be logged into your home network, and have python and git installed https://www.python.org, https://git-scm.com).

NB! Do not run this suite in a network unless you have consent. Some modules include disturbing functionality and could get you in trouble.

To use it; download this entire folder and run main.py. This can be done by point-and-click or from the terminal. 

1. Download or clone repository:
``` 
   git clone https://github.com/hambjo/VScan
```
2. Change location into the folder manually or via command:
```
   cd VScan
```
3. Use a virtual environment (optional)
```
   python -m venv .venv
   source .venv/bin/activate
   .venv/bin/activate  # Windows
```
4. Download dependencies:
```
   python -m pip install -r requirements.txt
```
5. Start the main script. To run VScan with all of VScans functionality you need to run it with superuser privileges. To do this in Windows you can right-click command prompt and run as administrator:
```
   python main.py
   sudo python main.py  # How to run with super user privileges on Linux and MacOS
```
