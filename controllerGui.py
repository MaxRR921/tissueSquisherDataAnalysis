import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import controller
from threading import Thread
#TODO: take out unnecessary imports

class ControllerGui:
    def __init__(self):
        self.micrometerController = controller.Controller()
        self.root = tk._default_root

    def __micrometerButtons(self):
        self.frameMicrometerMenu = tk.Frame(self.root, width=300, height=300)
        self.frameMicrometerMenu.config(bg="blue")
        self.frameMicrometerMenu.pack(side='left')
        self.frameMicrometerMenu.pack_propagate(False)
        self.__setHeightFrame()
            
    def run(self):
        self.ser = self.micrometerController.getSerialPort()
       
        self.__micrometerButtons()
        self.__topMenu()
                
    def __setHeightFrame(self):
     
        heightFrame = tk.Frame(self.frameMicrometerMenu, width=100, height=100)
        heightFrame.config(bg="green")
        heightFrame.pack(side="left")
        heightFrame.pack_propagate(False)

        setHeightLabel = tk.Label(heightFrame, text="Set the height")
        inputtxt = tk.Text(heightFrame, height = 1, width = 10) 
        
        

        setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [self.__goToHeight(inputtxt.get("1.0", "end-1c"))])
        setHeightButton.pack(side="bottom")
        inputtxt.pack(side="bottom")
        setHeightLabel.pack(side="top")
    
    def __goToHeight(self, inputHeight):
        thread = Thread(target = self.micrometerController.goToHeight, args=[inputHeight])
        thread.start()

    def __topMenu(self):
        self.frameTopMenu = tk.Frame(self.frameMicrometerMenu, width=250, height=80)
        self.frameTopMenu.config(bg="grey")
        self.frameTopMenu.pack(side='top', anchor='nw')
        self.frameTopMenu.pack_propagate(False)
        self.__startMicrometerButton()
        self.__disableMicrometerButton()
        self.__setMicrometerHomeButton()

    def __setMicrometerHomeButton(self):
        setMicrometerHomeButton = tk.Button(self.frameTopMenu, text="Set position as home", command=lambda: [self.micrometerController.setHome()])
        setMicrometerHomeButton.pack(side="left")
    def __startMicrometerButton(self):
        
        micrometerControlButton = tk.Button(self.frameTopMenu, text="Start micrometer", command=lambda: [self.__startMicrometer()])
        micrometerControlButton.pack(side="left")


    def __startMicrometer(self):
            thread = Thread(target = self.micrometerController.goHome, args=[])
            thread.start()

    def __disableMicrometerButton(self):
        micrometerEnterDisableStateButton = tk.Button(self.frameTopMenu, text="micrometer enter disable state", command=lambda: [self.micrometerController.disable()])
        micrometerEnterDisableStateButton.pack(side="left")

