import tkinter as tk
from gui import ScannerGUI

def main():
    root = tk.Tk()
    gui = ScannerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
