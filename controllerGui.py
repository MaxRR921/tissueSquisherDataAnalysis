import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import controller
from threading import Thread
#TODO: take out unnecessary imports

#WARNING DOESNT CLOSE MICROMETER UNTIL MAIN GUI WINDOW IS CLOSED
class ControllerGui:
    def __init__(self):
        micrometerController = controller.Controller()
        self.window = tk.Tk()
        self.window.title = ("Micrometer Control")
        self.window.geometry = ("400x400")
        self.ser = micrometerController.getSerialPort()
        self.__micrometerButtons()
        self.__topMenu()

        self.__run()



    def __micrometerButtons(self):
        frameMicrometerMenu = tk.Frame(self.window, width=100, height=200)
        frameMicrometerMenu.config(bg="blue")
        frameMicrometerMenu.pack(side='bottom')
        frameMicrometerMenu.pack_propagate(False)
        self.__setHeightFrame(frameMicrometerMenu)
            
    def __run(self):
        self. window.mainloop()
                
    def __setHeightFrame(self, frameMicrometerMenu):
        heightFrame = tk.Frame(self.frame, width=100, height=100)
        heightFrame.config(bg="green")
        heightFrame.pack(side="left")
        heightFrame.pack_propagate(False)

        setHeightLabel = tk.Label(self.heightFrame, text="Set the height")
        inputtxt = tk.Text(self.heightFrame, height = 1, width = 10) 
        
        setHeightButton = tk.Button(self.heightFrame, text="goTo", command=lambda: [controller.goToHeight(inputtxt.get("1.0", "end-1c") , self.ser)])
        setHeightButton.pack(side="bottom")
        inputtxt.pack(side="bottom")
        setHeightLabel.pack(side="top")
    
    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=500, height=80)
        frameTopMenu.config(bg="red")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)
        self.__startMicrometerButton(frameTopMenu)
        self.__micrometerEnterDisableStateButton(frameTopMenu, self.window, self.ser)

    def __startMicrometerButton(self, frameTopMenu):
        # def __startMicrometer(self):
        #     thread = Thread(target = controller.goHome, args=[self.ser])
        #     thread.start()
        micrometerControlButton = tk.Button(frameTopMenu, text="Start micrometer", command=lambda: [controller.goHome(self.ser)])
        micrometerControlButton.pack(side="left")

    def micrometerEnterDisableStateButton(self, frameTopMenu):
        micrometerEnterDisableStateButton = tk.Button(frameTopMenu, text="micrometer enter disable state", command=lambda: [controller.disable(self.ser)])
        micrometerEnterDisableStateButton.pack(side="left")




# #micrometer control window buttons:
# # def micrometerButtons(window, ser) : 
# #     micrometerMenu = tk.Frame(window, width=100, height=200)
# #     micrometerMenu.config(bg="blue")
# #     micrometerMenu.pack(side='bottom')
# #     micrometerMenu.pack_propagate(False)
#      setHeightFrame(micrometerMenu, window, ser)
    
    


# def topMenu(window, ser):
#     frameTopMenu = tk.Frame(window, width=500, height=80)
#     frameTopMenu.config(bg="red")
#     frameTopMenu.pack(side='top')
#     frameTopMenu.pack_propagate(False)
#     startMicrometerButton(frameTopMenu, window, ser)
#     micrometerEnterDisableStateButton(frameTopMenu, window, ser)


# def setHeightFrame(frame, window, ser):
#     heightFrame = tk.Frame(frame, width=100, height=100)
#     heightFrame.config(bg="green")
#     heightFrame.pack(side="left")
#     heightFrame.pack_propagate(False)

#     setHeightLabel = tk.Label(heightFrame, text="Set the height")
#     inputtxt = tk.Text(heightFrame, height = 1, width = 10) 
     
#     setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [controller.goToHeight(inputtxt.get("1.0", "end-1c") , ser)])
#     setHeightButton.pack(side="bottom")
#     inputtxt.pack(side="bottom")
#     setHeightLabel.pack(side="top")



# def startMicrometerButton(frameTopMenu, window, ser):
#     def startMicrometer():
#         thread = Thread(target = controller.goHome, args=[ser])
#         thread.start()
#     micrometerControlButton = tk.Button(frameTopMenu, text="Start micrometer", command=lambda: [controller.goHome(ser)])
#     micrometerControlButton.pack(side="left")

# def micrometerEnterDisableStateButton(frameTopMenu, window, ser):
#     micrometerEnterDisableStateButton = tk.Button(frameTopMenu, text="micrometer enter disable state", command=lambda: [controller.disable(ser)])
#     micrometerEnterDisableStateButton.pack(side="left")

