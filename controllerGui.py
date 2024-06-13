import tkinter as tk
from threading import Thread
import time  # Import the time module
import controller
from plotterGUI import PlotterGUI
from movePlanner import MovePlanner

class ControllerGui:
    def __init__(self):
        self.micrometerController = controller.Controller()
        self.window = None  # Move initialization to run method
        self.ser = self.micrometerController.getSerialPort()

        self.heightLabel = None  # Initialize the height label as None
        self.plotWindow = None
        self.plotterGui = None
        self.startTime = None  # Initialize start time

        self.movePlanner = MovePlanner()  # Initialize MovePlanner

    def __micrometerButtons(self):
        frameMicrometerMenu = tk.Frame(self.window, width=100, height=200)
        frameMicrometerMenu.config(bg="blue")
        frameMicrometerMenu.pack(side='bottom')
        frameMicrometerMenu.pack_propagate(False)
        self.__setHeightFrame(frameMicrometerMenu)
            
    def run(self):
        self.window = tk.Tk()  # Initialize the window here
        self.window.title("Micrometer Control")
        self.window.geometry("400x400")
        self.__micrometerButtons()
        self.__topMenu()
        self.__createHeightLabel()  # Add height label to the GUI
        self.window.mainloop()
                
    def __setHeightFrame(self, frameMicrometerMenu):
        heightFrame = tk.Frame(frameMicrometerMenu, width=100, height=100)
        heightFrame.config(bg="green")
        heightFrame.pack(side="left")
        heightFrame.pack_propagate(False)

        setHeightLabel = tk.Label(heightFrame, text="Set the height")
        inputTxt = tk.Text(heightFrame, height=1, width=10) 
        setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [self.__goToHeight(inputTxt.get("1.0", "end-1c"))])
        setHeightButton.pack(side="bottom")
        inputTxt.pack(side="bottom")
        setHeightLabel.pack(side="top")
    
    def __goToHeight(self, inputHeight):
        if self.plotterGui:
            self.plotterGui.resetPlot()
        self.startTime = time.time()  # Record the start time
        thread = Thread(target=self.micrometerController.goToHeight, args=[inputHeight, self])
        thread.start()

    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=500, height=80)
        frameTopMenu.config(bg="red")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)
        self.__startMicrometerButton(frameTopMenu)
        self.__disableMicrometerButton(frameTopMenu)
        self.__plotHeightButton(frameTopMenu)
        self.__openPlanningWindowButton(frameTopMenu)  # Add the planning window button

    def __startMicrometerButton(self, frameTopMenu):
        micrometerControlButton = tk.Button(frameTopMenu, text="Start micrometer", command=lambda: [self.micrometerController.goHome()])
        micrometerControlButton.pack(side="left")

    def __disableMicrometerButton(self, frameTopMenu):
        micrometerEnterDisableStateButton = tk.Button(frameTopMenu, text="micrometer enter disable state", command=lambda: [self.micrometerController.disable()])
        micrometerEnterDisableStateButton.pack(side="left")
        
    def __plotHeightButton(self, frameTopMenu):
        plotHeightButton = tk.Button(frameTopMenu, text="Plot Motion", command=self.__openPlotWindow)
        plotHeightButton.pack(side="left")

    def __openPlanningWindowButton(self, frameTopMenu):
        planningWindowButton = tk.Button(frameTopMenu, text="Open Planning Window", command=lambda: self.movePlanner.openPlanningWindow(self.window))
        planningWindowButton.pack(side="left")

    def __openPlotWindow(self):
        if self.plotWindow is None or not self.plotWindow.winfo_exists():
            self.plotWindow = tk.Toplevel(self.window)
            self.plotterGui = PlotterGUI(self.plotWindow)

    def __createHeightLabel(self):
        self.heightLabel = tk.Label(self.window, text="Height: 0.0000 mm", font=("Helvetica", 16))
        self.heightLabel.place(relx=0.5, rely=0.5, anchor='center')
        
    def updateHeightLabel(self, height):
        if self.heightLabel:
            self.heightLabel.config(text=f"Height: {height:.4f} mm")
        if self.plotterGui:
            currentTime = time.time()
            relativeTime = currentTime - self.startTime  # Calculate relative time
            self.plotterGui.updatePlot(relativeTime, height)

if __name__ == "__main__":
    app = ControllerGui()
    app.run()
