import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import polarimeter
from threading import Thread
#TODO: take out unnecessary imports

#WARNING DOESNT CLOSE MICROMETER UNTIL MAIN GUI WINDOW IS CLOSED
def run():
    window = polarimeterControlWindowSetup()
    window.mainloop()


def polarimeterControlWindowSetup():
    window = tk.Tk()

    window.title("Polarimeter")

    window.geometry("400x400")
    
    poalrimeterButtons(window)
    topMenu(window)
    return window


#micrometer control window buttons:
def poalrimeterButtons(window) : 
    menu = tk.Frame(window, width=100, height=200)
    menu.config(bg="blue")
    menu.pack(side='bottom')
    menu.pack_propagate(False)
    


def topMenu(window):
    frameTopMenu = tk.Frame(window, width=500, height=80)
    frameTopMenu.config(bg="red")
    frameTopMenu.pack(side='top')
    frameTopMenu.pack_propagate(False)
    startPolarimeterButton(frameTopMenu, window)






def startPolarimeterButton(frameTopMenu, window):
    def startPolarimeter():
        thread = Thread(target = polarimeter.start, args=[10])
        thread.start()
       
    micrometerControlButton = tk.Button(frameTopMenu, text="Start polarimeter", command=lambda: [startPolarimeter()])
    micrometerControlButton.pack(side="left")



