import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import controller
from threading import Thread
#TODO: take out unnecessary imports

#WARNING DOESNT CLOSE MICROMETER UNTIL MAIN GUI WINDOW IS CLOSED
class ControllerGui:
    def __init__(self):
        self.micrometerController = controller.Controller()
       
    def __micrometerButtons(self):
        frameMicrometerMenu = tk.Frame(self.window, width=100, height=200)
        frameMicrometerMenu.config(bg="blue")
        frameMicrometerMenu.pack(side='bottom')
        frameMicrometerMenu.pack_propagate(False)
        self.__setHeightFrame(frameMicrometerMenu)
            
    def run(self):
        self.window = tk.Tk()
        self.window.title = ("Micrometer Control")
        self.window.geometry = ("400x400")
        self.ser = self.micrometerController.getSerialPort()
       
        self.__micrometerButtons()
        self.__topMenu()
        self. window.mainloop()
                
    def __setHeightFrame(self, frameMicrometerMenu):
        heightFrame = tk.Frame(frameMicrometerMenu, width=100, height=100)
        heightFrame.config(bg="green")
        heightFrame.pack(side="left")
        heightFrame.pack_propagate(False)

        setHeightLabel = tk.Label(heightFrame, text="Set the height")
        inputtxt = tk.Text(heightFrame, height = 1, width = 10) 
        

        setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [self.micrometerController.goToHeight(inputtxt.get("1.0", "end-1c"))])
        setHeightButton.pack(side="bottom")
        inputtxt.pack(side="bottom")
        setHeightLabel.pack(side="top")
    
    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=500, height=80)
        frameTopMenu.config(bg="red")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)
        self.__startMicrometerButton(frameTopMenu)
        self.__disableMicrometerButton(frameTopMenu)

    def __startMicrometerButton(self, frameTopMenu):
        # def __startMicrometer(self):
        #     thread = Thread(target = controller.goHome, args=[self.ser])
        #     thread.start()
        micrometerControlButton = tk.Button(frameTopMenu, text="Start micrometer", command=lambda: [self.micrometerController.goHome()])
        micrometerControlButton.pack(side="left")

    def __disableMicrometerButton(self, frameTopMenu):
        micrometerEnterDisableStateButton = tk.Button(frameTopMenu, text="micrometer enter disable state", command=lambda: [self.micrometerController.disable()])
        micrometerEnterDisableStateButton.pack(side="left")

