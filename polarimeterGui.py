import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import polarimeter
from threading import Thread
#TODO: take out unnecessary imports

#WARNING DOESNT CLOSE MICROMETER UNTIL MAIN GUI WINDOW IS CLOSED
class PolarimeterGui():
    def __init__(self):
        polar = polarimeter.Polarimeter()

    def run(self):
        self.window = tk.Tk()

        self.window.title("Polarimeter")

        self.window.geometry("400x400")
        
        self.__poalrimeterButtons()
        self.__topMenu()
        self.window.mainloop()

    #polarimeter control window buttons:
    def __poalrimeterButtons(self): 
        menu = tk.Frame(self.window, width=100, height=200)
        menu.config(bg="blue")
        menu.pack(side='bottom')
        menu.pack_propagate(False)

    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=500, height=80)
        frameTopMenu.config(bg="red")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)
        self.__startPolarimeterButton(frameTopMenu)

    def __startPolarimeterButton(self, frameTopMenu):
        
        micrometerControlButton = tk.Button(frameTopMenu, text="Start polarimeter", command=lambda: [self.__startPolarimeter()])
        micrometerControlButton.pack(side="left")

    def __startPolarimeter(self):
        thread = Thread(target = self.polar.start, args=[10])
        thread.start()