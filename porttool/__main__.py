#!/usr/bin/env python3
from tkinter import Tk
from .ui import MyUI
from os import name

if name == 'nt':
    import ctypes
    from multiprocessing.dummy import freeze_support

    freeze_support()


def main():
    root = Tk()
    root.title("MTK Port Tool")
    # root.geometry("860x480")

    myapp = MyUI(root)
    myapp.pack(side='top', fill='both', padx=5, pady=5, expand='yes')

    # Fix high dpi
    if name == 'nt':
        # Tell system using self dpi adapt
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # Get screen resize scale factor
        scalefactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        root.tk.call('tk', 'scaling', scalefactor / 75)

    root.update()
    root.mainloop()
