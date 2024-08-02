# IoT_Vulnerability_Scanner
This repository includes Python files that try to detect vulnerabilities in devices at your home network. (the computer deploying this must be logged into your home network, and have python and git installed https://www.python.org, https://git-scm.com).

To use it; download this entire folder and run main.py. This can be done by point-and-click or from the terminal. 

1. Download or clone repository:
``` 
   git clone https://github.com/hambjo/IoT_Vulnerability_Scanner
```
2. Change location into the folder manually or via command:
```
   cd IoT_Vulnerability_Scanner
```
3. Use a virtual environment (optional)
```
   python -m venv .venv
   source .venv/bin/activate
   .venv/bin/activate # Windows
```
4. Download dependencies:
```
   python -m pip install -r requirements.txt
```
5. Start the main script regularly (or with super user privileges to utilise all of VScans functionality. To do this in Windows you can right-click command prompt and run as administrator):
```
   python main.py (sudo python main.py)
```
