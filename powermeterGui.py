import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import powermeter
from threading import Thread
#TODO: take out unnecessary imports

#WARNING DOESNT CLOSE MICROMETER UNTIL MAIN GUI WINDOW IS CLOSED
class PowermeterGui():
    def __init__(self):
        self.power = powermeter.Powermeter()
        self.root = tk._default_root

    def run(self): 
        self.__powermeterButtons()
        self.__topMenu()

    #polarimeter control window buttons:
    def __powermeterButtons(self): 
        menu = tk.Frame(self.root, width=100, height=200)
        menu.config(bg="blue")
        menu.pack(side='bottom')
        menu.pack_propagate(False)

    def __topMenu(self):
        frameTopMenu = tk.Frame(self.root, width=500, height=80)
        frameTopMenu.config(bg="red")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)
        self.__startPolarimeterButton(frameTopMenu)

    def __startPolarimeterButton(self, frameTopMenu):
        
        micrometerControlButton = tk.Button(frameTopMenu, text="Start polarimeter", command=lambda: [self.__startPowerMeter()])
        micrometerControlButton.pack(side="left")

    def __startPowerMeter(self):
        thread = Thread(target = self.power.start, args=[])
        thread.start()