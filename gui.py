import numpy as np
import tkinter as tk
import controller
import powermeter
from plotter import Plot2D
import time
import move
import moveGui
import threading
from tkinter import ttk
from ttkthemes import ThemedTk
import polarimeter
import angleFinder
import csv
import multiprocessing
import graphingProcess
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d

"""!THINKING MAYBE I SHOULD JUSt iNitiAlize all of the threads in init, then call them later"""


"""init initializes all of the gui elements, as well as the classes corresponding to every device
!it also initializs self.phase and self.strain np.arrays which is kind of weird
it then adds a default move to the move list, which is fine
after that it initializes some more gui elements.

!THIS METHOD ALSO STARTS THE POWERMETERS THREAD, WHICH THAT THREAD THEN SPAWNS A THREAD FOR EACH POWERMETER AND WAITS UNTIL both of those join.

!starts updating all of the graphs. this is bad because that method sucks rn. because of a few reasons.
"""
class Gui:
    def __init__(self):
        #initializing UI
        self.window = ThemedTk(theme="breeze")
        self.root = tk._default_root #same as window!
        self.window.title("Data GUI")
        self.window.geometry("800x800")
        self.numExecutions = 1
        self.signalGraph = multiprocessing.Queue()
        self.signalAngleFinder = threading.Event()
        self.signalAngleFinder.clear()


        #Initializing device classes.
        try:
            self.micrometerController = controller.Controller()
        except:
            print("Micrometer Connection Error")
            self.micrometerController = None

        self.polarimeter = None
        try:
            self.polarimeter = polarimeter.Polarimeter(self.micrometerController)
            self.polarimeterThread = threading.Thread(target=self.polarimeter.start, args=[])
        except:
            print("Polarimeter Connection Error")


        try:
            self.powermeter = powermeter.Powermeter()
            self.powermeterThread = threading.Thread(target=self.powermeter.start, args=[])
            print("Powermeters connected successfully")
        except:
            print("Powermeter Connection Error. You need two powermeters connected at all times.")
            self.powermeter = None

        # Event booleans
        self.updatingPlots = threading.Event() 
        self.updatingPlots.clear()
        self.triedMicrometer = False
        self.executed = threading.Event()
        self.executed.clear()
        self.startedPolarimeter = False

        #lists for phase and strain...bad.
        self.phase = np.array(np.zeros)
        self.strain = np.array(np.zeros)

        #setting up powermeter text in ui
        self.power1Text = tk.StringVar()
        self.power2Text = tk.StringVar()
        self.s1Text = tk.StringVar()
        self.s2Text = tk.StringVar()
        self.s3Text = tk.StringVar()
        self.power1Text.set("p1 not reading")
        self.power2Text.set("p2 not reading") 




        #one move by default
        defualtMove = move.Move(self.micrometerController)
        self.moveList = [defualtMove]

        if self.powermeter is not None:
            self.powermeterThread.start()

        #plots:
        self.plotList = []
        self.polPlot = None
        self.powerPlot = None
        self.micrometerPlot = None
        self.pow1Plot = None
        self.pow2Plot = None
        self.noisePlotPowDif = None
        self.noisePlotPow1 = None
        self.noisePlotPow2 = None 
        #list of times recorded
        self.timeList = []
        
        self.execTime = 1000

        self.deltaPowerDifferences = []


        self.pyqt_process = None

        # adding listFrame
        self.listFrame = tk.Frame(self.window, width=800, height=1000)  # Adjust the width here for the left panel
        self.listFrame.grid(row=0, column=0, columnspan= 2, rowspan=2, sticky="nsew")
        self.listFrame.grid_propagate(False)



        # Create top menu frame
        self.topMenuFrame = tk.Frame(self.window, height=30, background="light grey")  # Adjust the height here
        self.topMenuFrame.grid(row=0, column=0, columnspan=2, sticky="new")
        self.topMenuFrame.grid_propagate(False)
        self.addTopMenuButtons()

        self.readSavedIdealAlpha()
        self.readSavedIdealBeta() 

        #create bottomFrame 
        self.bottomFrame = tk.Frame(self.window, height=80, background="light grey")
        self.bottomFrame.grid(row=1, column=0, columnspan=2, sticky='sew')
        self.bottomFrame.grid_propagate(False)
        self.addBottomFrameButtons(self.bottomFrame)

        #making rows/columns expandable...
        self.window.columnconfigure(0, weight=1)  # Make the list frame column expandable
        self.window.columnconfigure(1, weight=3)  # Make the main frame column expandable
        self.window.rowconfigure(0, weight=1)     # Make the row expandable
        self.window.rowconfigure(1, weight=2)

        #create the move list gui elements
        self.moveGui = moveGui.MoveGui(self.listFrame, self, self.moveList, 100, width=500)

        self.angleFind = angleFinder.AngleFinder()


        #updating all plots 
        self.root.protocol('WM_DELETE_WINDOW', self.stop)
        self.root.after(10, self.updatePlotsFromData)
        self.stopExecution = False




    """stop tells the powermeters to stop collecting data. 
    !There is no detection right now of whether the powermeters are even connected...
    it then tries to join the execution thread, which is opened to begin the execution of the moves !REMOVE FROM 
    TRY CATCH? and make if statement
    !THEN JOINS POLARIMETER THREAD... I FEEL LIKE THIS SHOULD FOLLOW A SIMILAR THING TO POWERMETER THREADS IDK
    WHY ITS IN A TRY CATCH RIGHT NOW...
    then tells polaremter and micrometer to stop and tells powermeter threads to join

    THis method is in need of a restructure... why does some stuff lie in try catches, should just put in if's
    """
    def stop(self):
        if self.powermeter is not None:
            self.powermeter.stop()
        self.stopExecution = True
        self.updatingPlots.clear() 
        try:
            self.executeThread.join()
        except:
            print("NOT currently executing")
        try:
            self.polarimeterThread.join() #needs to join so that it's not initializing when i tell it to stop...
        except:
            print("polarimeter thread not yet started")
        if(self.polarimeter is not None):
            self.polarimeter.stop()
        else:
            print("No polarimeter Connected")
        if(self.micrometerController is not None):
            self.micrometerController.stop()
        else:
            print("No micrometer connected")

        self.powermeterThread.join()


        if self.pyqt_process is not None and self.pyqt_process.is_alive():
                print("Terminating PyQt process...")
                self.pyqt_process.terminate()
                self.pyqt_process.join()

        self.root.destroy()

    """run begins the main loop. this is fine just a tkinter thing"""
    def run(self):
        self.window.mainloop()

    """addTopMenuButtons is executed from init, calls the methods that create all of the buttons"""
    def addTopMenuButtons(self):
        self.__browseDataFileButton(self.topMenuFrame)
        self.__startGraphingButton(self.topMenuFrame)
        self.__findAngleButton(self.topMenuFrame)
        self.alphaLabel = ttk.Label(self.topMenuFrame, text="Ideal Alpha: N/A")
        self.alphaLabel.pack(side='left')
        self.betaLabel = ttk.Label(self.topMenuFrame, text="Ideal Ideal Beta: N/A")
        self.betaLabel.pack(side='left')


    #ALL BUTTONS IN TOP MENU
    """browseDataFile button creates the button for browsing for the data files."""
    def __browseDataFileButton(self, frameTopMenu):
        browseDataFileButton = ttk.Button(frameTopMenu, text="browse for data file", command=lambda: self.__browseFile())
        browseDataFileButton.pack(side='left')

    """browseFile opens the file browser, is executed from the button"""
    def __browseFile(self):
        self.filePath = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if self.filePath:
            self.__plot()

    """startpolarimeterthread starts the thread for data collection from the powlarimeter. This thread runs polarimeter.start"""
    def __startPolarimeterThread(self):
        print("SHOULD START")
        self.polarimeterThread = threading.Thread(target=self.polarimeter.start, args=[])
        self.polarimeterThread.start()

    def __startGraphingButton(self, frameTopMenu):
        startPyQtButton = ttk.Button(frameTopMenu, text='Start PyQt Plot', command=lambda: self.startPyqtProcess())
        startPyQtButton.pack(side="left")

    def __findAngleButton(self, frameTopMenu):
        findAngleButton = ttk.Button(frameTopMenu, text='open angle finder', command=lambda: self.findAngle())
        findAngleButton.pack(side="left")

    def startPyqtProcess(self):
        """Spawn a separate process that runs the PyQt/pyqtgraph event loop."""
        # If not already running (or if the process has ended), start it
        if self.pyqt_process is None or not self.pyqt_process.is_alive():
            print("Starting PyQt process...")
            if not self.polarimeter == None:
                self.pyqt_process = multiprocessing.Process(target=graphingProcess.run_pyqt_app,
                                                            args=(self.signalGraph, self.micrometerController.plotQueue, self.powermeter.device1PlotQueue, self.powermeter.device2PlotQueue, self.polarimeter.dataAnalyzer.phaseQueue, self.polarimeter.dataAnalyzer.strainQueue))
                self.pyqt_process.start()
            elif self.polarimeter == None:
                self.pyqt_process = multiprocessing.Process(target=graphingProcess.run_pyqt_app,
                                                            args=(self.signalGraph, self.micrometerController.plotQueue, self.powermeter.device1PlotQueue, self.powermeter.device2PlotQueue, None, None))
                self.pyqt_process.start()
        else:
            print("PyQt process is already running!")        


    """adds all of the buttons in the bottom frame"""
    def addBottomFrameButtons(self, listFrame):
        numExec = tk.StringVar()
        timeRecord = tk.StringVar()
        ttk.Entry(listFrame, textvariable=numExec).grid(row=2, column=1, sticky='sw', pady=5)
        ttk.Entry(listFrame, textvariable=timeRecord).grid(row=1, column=4, sticky='sw', pady=5)
        listFrame.grid_rowconfigure(0, weight=1)
        listFrame.grid_rowconfigure(1, weight=0)
        listFrame.grid_columnconfigure(1, weight=0)
        listFrame.grid_columnconfigure(2, weight=1)
        listFrame.grid_columnconfigure(3, weight=2)

        executeAllMovesButton = ttk.Button(listFrame, text='execute all moves', command=lambda: (self.saveNumExecutions(numExec), self.startExecuteThread(self.moveList, True)))
        executeAllMovesButton.grid(row=2, column=0, sticky='sw', pady=5, padx=30)

        recordNoiseButton = ttk.Button(listFrame, text='Record for Time:', command=lambda: (self.saveExecuteTime(timeRecord), self.startNoiseThread()))
        recordNoiseButton.grid(row=1, column=3, sticky='sw', pady=5, padx=30)

        addMoveButton = ttk.Button(listFrame, text='add move', command=lambda: self.__addMove(listFrame))
        addMoveButton.grid(row=1, column=0, sticky='sw', pady=5, padx=30)

        stopExecutionButton = ttk.Button(listFrame, text='Stop Execution', command=lambda: setattr(self, 'stopExecution', True))
        stopExecutionButton.grid(row=1, column=1, sticky='sw', pady=5, padx=30)

        zeroButton = ttk.Button(listFrame, text='Zero Force', command=lambda: self.__zeroForce())
        zeroButton.grid(row=1, column=3, sticky='sw', pady=5, padx=70)


        raiseMicrometerButton = ttk.Button(listFrame, text='Raise Micrometer', command=lambda: self.__raiseMicrometer())
        raiseMicrometerButton.grid(row=1, column=2, sticky='sw', pady=5, padx=30)

        if self.powermeter is not None:
            power1Text = ttk.Label(listFrame, textvariable=self.power1Text).grid(row=2, column=3, sticky = 'w', pady=5, padx=2)
            power1Text = ttk.Label(listFrame, textvariable=self.power2Text).grid(row=2, column=3, sticky = 'e', pady=5, padx=10)
            timesText = ttk.Label(listFrame, text='times').grid(row=2, column=2, sticky= 'w', pady=5, padx=5)

        if self.polarimeter is not None:
            s1Text = ttk.Label(listFrame, textvariable=self.s1Text).grid(row=1, column=2, sticky = 'w', pady=5, padx=.01)
            s2Text = ttk.Label(listFrame, textvariable=self.s2Text).grid(row=1, column=3, sticky = 'w', pady=5, padx=.01)
            s3Text = ttk.Label(listFrame, textvariable=self.s3Text).grid(row=1, column=4, sticky = 'w', pady=5, padx=.01)


    """ saveNumExecutions is called when executeall is pressed, saves the number of executions the user entered
    in the little box at the bottom, checks for invalid input in the textbox."""
    def saveNumExecutions(self, numExec):
        try:
            self.numExecutions = int(numExec.get())
            print(f"Saved number of executions: {self.numExecutions}")
        except ValueError:
            print("Invalid input, please enter a valid number")

    """ saveExecutTime is called when Record for time is pressed, saves the time the user entered
    in the little box at the bottom, checks for invalid input in the textbox."""
    def saveExecuteTime(self, execTime):
        try:
            self.execTime = int(execTime.get())
            print(f"Saved number of executions: {self.execTime}")
        except:
            print("Invalid input, please enter a valid number")

    def __raiseMicrometer(self):
        raiseMove = move.Move(self.micrometerController)
        raiseMove.velocity = "1"
        raiseMove.targetHeight = "12"
        listTemp = []
        self.numExecutions = 1
        listTemp.append(raiseMove)
        self.startExecuteThread(listTemp, False)




    """startExecuteThread resets all of the constantly polling plots... starts the execute thread which calls 
    thecollect method. 
    !! should make it just use self.movelist...."""
    def startExecuteThread(self, moveList, collectData):
        self.signalGraph.put("STOP")
        self.executeThread = threading.Thread(target=self.__collect, args=[moveList, collectData])
        self.executeThread.start()

    def startNoiseThread(self):
        self.signalGraph.put("STOP")
        for plot in self.plotList:
            plot.resetPlot()
        self.noiseThread = threading.Thread(target=self.__collectNoise)
        self.noiseThread.start()

    def __zeroForce(self):
        print("ZEROED FORCE")

    def __collectNoise(self):
        print("collecting data")
            
        if not self.powermeter.updatingDevice1CsvQueue.is_set():
            self.powermeter.updatingDevice1CsvQueue.set()
        
        if not self.powermeter.updatingDevice2CsvQueue.is_set():
            self.powermeter.updatingDevice2CsvQueue.set()

        if self.polarimeter is not None:
            if not self.polarimeter.updatingCsvQueue.is_set():
                self.polarimeter.updatingCsvQueue.set()

        if self.pyqt_process is not None and self.pyqt_process.is_alive():
            self.micrometerController.updatingPlotQueue.set()
            self.powermeter.updatingDevice1PlotQueue.set()
            self.powermeter.updatingDevice2PlotQueue.set()

        #POLARIMETER NEEDS TO START RUNNING BEFORE MOVES EXECUTE. IT DOESN'T CONSTANTLY RUN LIKE THE POWERMETER.
        if(self.polarimeter is not None):
            self.polarimeter.run = True
            self.__startPolarimeterThread()
        else:
            print("No polarimeter Connected")

        currTime = time.time()
        t = self.execTime
        start_time = time.time()
        end_time = start_time 
        if not self.updatingPlots.is_set():
            self.updatingPlots.set()
        while(end_time - start_time < t):
           end_time = time.time() 
           print("waiting")
        self.updatingPlots.clear()
        try:
            self.noisePlotPowDif.generateCsvFromPlot("power dif vs. time.csv")
        except:
            print("plot not open")
        try:
            self.noisePlotPow1.generateCsvFromPlot("power 1 vs. time.csv")
        except:
            print("plot not open")

        while(time.time() - currTime < self.execTime and not self.stopExecution):
            print("collecting noise data")
        
        
        self.executed.set()
        # time.sleep(2)
        try:
            self.noisePlotPow2.generateCsvFromPlot("power 2 vs. time.csv")
        except:
            print("plot not open")

        self.micrometerController.updatingCsvQueue.clear()
        self.micrometerController.updatingPlotQueue.clear()
        self.powermeter.updatingDevice1CsvQueue.clear()
        self.powermeter.updatingDevice2CsvQueue.clear()
        self.powermeter.updatingDevice1PlotQueue.clear()
        self.powermeter.updatingDevice2PlotQueue.clear()
        if self.polarimeter is not None:
            self.polarimeter.dataAnalyzer.finishAnalyzeDataSignal.wait()
            self.polarimeter.dataAnalyzer.finishAnalyzeDataSignal.clear()
            self.polarimeter.updatingCsvQueue.clear()
        self.generateCsvs()
        print("DONE")


    #STRANGE: NOTE: when doing this sometimes the pyqt plots just don't do anything. Maybe add a little wait?

    # Need to figure out how to get the data into the angleFinder script. We need to get the minumum and maximum from the power difference!

            #plan: 
            # two new queues in the powermeters, pop them off in here and interpolate just like I did for the plot. I feel like this is good because the thing 

    def findAngle(self):
        powerRatios = []
        new_window = tk.Toplevel()
        new_window.title("Angle Data Collection")
        new_window.geometry("300x200")
        angle = -20

        rotate_label = ttk.Label(new_window, text=f"Rotate to {angle} degrees.")
        rotate_label.pack(pady=(10, 0))

        # Min Height
        ttk.Label(new_window, text="Min Height:").pack(pady=(10, 0))
        min_height_entry = ttk.Entry(new_window)
        min_height_entry.pack()

        # Max Height
        ttk.Label(new_window, text="Max Height:").pack(pady=(10, 0))
        max_height_entry = ttk.Entry(new_window)
        max_height_entry.pack()


        # Dropdown for saving target: alpha or beta
        ttk.Label(new_window, text="Save to:").pack(pady=(10, 0))
        save_target = tk.StringVar(value="alpha")  # default value
        save_dropdown = ttk.Combobox(new_window, textvariable=save_target, state="readonly")
        save_dropdown['values'] = ("alpha", "beta")
        save_dropdown.pack()



        # Begin Collection Button
        def begin_collection():
            nonlocal angle
            min_height = str(min_height_entry.get())
            max_height = str(max_height_entry.get())
            self.signalAngleFinder.clear()

            if float(max_height) <= float(min_height):
                print("can't enter this height")
                return

            listTemp = []
            positionMove = move.Move(self.micrometerController)
            positionMove.velocity = "1"
            positionMove.targetHeight = max_height
            listTemp.append(positionMove)
            self.numExecutions = 1
            self.startExecuteThread(listTemp, False)
            self.signalAngleFinder.wait()
            self.signalAngleFinder.clear()

            time.sleep(3) #need time to reinitialize everything
            listTemp = []

            lowerMove = move.Move(self.micrometerController)
            lowerMove.velocity = ".1" 
            lowerMove.targetHeight = min_height
            listTemp.append(lowerMove)

            raiseMove = move.Move(self.micrometerController)
            raiseMove.velocity = ".1"
            raiseMove.targetHeight = max_height
            listTemp.append(raiseMove)
            self.numExecutions = 3
            self.powermeter.updatingAngleQueues.set()
            print("Finding angle: ", self.powermeter.updatingAngleQueues.is_set())
            self.startExecuteThread(listTemp, True)
            self.signalAngleFinder.wait()
            self.signalAngleFinder.clear()
            self.powermeter.updatingAngleQueues.clear()
            print("Finding angle: ", self.powermeter.updatingAngleQueues.is_set())
            print("SHOULD NOW RAISE MICROMETER!!!")
            time.sleep(3)
            self.__raiseMicrometer()
            self.signalAngleFinder.wait()
            self.signalAngleFinder.clear()
            angle += 10 
            powerRatios.append(self.findDeltaPowerDif())
            if(angle > 20):
                rotate_label.config(text="compute the ideal angle")
            else:
                rotate_label.config(text=f"Rotate to {angle} degrees.")







        def start_collection_thread():
            self.angleThread = threading.Thread(target=begin_collection, args=[])
            self.angleThread.start()



        ttk.Button(new_window, text="Begin Collection", command=start_collection_thread).pack(pady=20)

        def show_angle():
            angle = self.angleFind.findAngle(powerRatios)

            self.angleFind.plot()
            ttk.Label(new_window, text=f"Ideal Angle: {angle:.2f}°").pack()
            print("SHOULD SAVE ANGLE", save_target.get())

            if save_target.get() == "alpha":
                self.updateIdealAlpha(angle)
            elif save_target.get() == "beta":
                self.updateIdealBeta(angle)

        ttk.Button(
            new_window,
            text="Compute Ideal Angle",
            command=show_angle
        ).pack()

    def findDeltaPowerDif(self):
        time1 = []
        power1 = []
        time2 = []
        power2 = []
        while not self.powermeter.angle1Queue.empty():
            x,y = self.powermeter.angle1Queue.get_nowait()
            time1.append(x)
            power1.append(y)
        while not self.powermeter.angle2Queue.empty():
            x,y = self.powermeter.angle2Queue.get_nowait()
            time2.append(x)
            power2.append(y)
        print("power 1: ", power1)
        print("power 2:", power2)

        interp_func = interp1d(time2, power2, kind='linear', fill_value='extrapolate')
        aligned_pow2 = interp_func(time1)
        diff = power1 / aligned_pow2
        deltaDiff = np.abs(np.max(diff) - np.min(diff))
        for i in range(50):
            print(deltaDiff)
        return deltaDiff



    # 2 things: 
    # 1. read for ideal alpha from file on startup, update label
    # 2. take in angle, write to file, update label

    def readSavedIdealAlpha(self):
        try:
            with open("idealAlpha.txt", "r") as f:
                alpha = f.read().strip()
            self.alphaLabel.config(text=f"Ideal Alpha: {alpha}°")
        except FileNotFoundError:
            self.alphaLabel.config(text="ideal alpha not saved")

    def readSavedIdealBeta(self):
        try:
            with open("idealBeta.txt", "r") as f:
                beta = f.read().strip()
            self.betaLabel.config(text=f"Ideal Beta: {beta}°")
        except FileNotFoundError:
            self.betaLabel.config(text="ideal beta not saved")

    def updateIdealAlpha(self, alpha):
        print("UPDATING IDEAL ALPHA!!!!!!!")
        try:
            with open("idealAlpha.txt", "w") as f:
                f.write(str(alpha))
            self.alphaLabel.config(text=f"Ideal Alpha: {alpha}°")
        except Exception as e:
            self.alphaLabel.config(text="Failed to save ideal alpha")
            print(f"Error saving alpha: {e}")



    def updateIdealBeta(self, beta):
        try:
            with open("idealBeta.txt", "w") as f:
                f.write(str(beta))
            self.betaLabel.config(text=f"Ideal Beta: {beta}°")
        except Exception as e:
            self.betaLabel.config(text="Failed to save ideal alpha")
            print(f"Error saving beta: {e}")








    """collect is a lot of logic. !should make it just use self.movelist
    if the plots currently aren't updating, it calls the recursive updatePlots function to update the plots 
    every 100 ms. Should just have this instead of having all plots update all of the time.
    then talls the polarimeter to start running, and starts its thread im thinking there is probably some cleaner logic
    for this. 
    !!in the for loop, it does every move the number of executions the user wants times. just calls move.execute 
     and if the program flags to stop execution of the move, it just breaks out of the loop a little haphazardly I 
      also should add a button for stopexecution. 
    !!! weird try catch for polarimeter.run i guess if the polarimeter is not there it shouldn't execute this.
.
     """
    """
    this starts the collection thread, each move.execute blocks the thread until the move completes 
    """

    #two options for the plotting: 
    #1. plots constantly update even when moves aren't executing 
    #2. only update when moves are executing 
    # conclusion: make both
    # how should we do it? 
    # 1. enable plotting button after window is open. This sends a signal to all devices saying that it's time to start adding to the queues
    # 2. Reset plots button: clears the plots
    # 3. if plots are disabled when execution is started, all of the plots are reset and enabled. 


    #collection sequence:
    #1. make a new flag: executing 
    #2. when executing is set, sensors add to their Queue.queue's 
    #3. When executing is set, sensors add to their multiprocessing.queue's
    #. when executed is set, gui takes all the sensor Queue.queue's and copies them to arrays, then writes the arrays to csv's (check if you
    # can write a queue directly to a csv. It will write micrometer position vs. power 1 and 2 to the csvs to start.)



    def __collect(self, moveList, collectData):
        print("collecting data")
        if collectData:
            if not self.updatingPlots.is_set():
                self.updatingPlots.set() 


            if not self.micrometerController.updatingCsvQueue.is_set():
                self.micrometerController.updatingCsvQueue.set()

            if not self.powermeter.updatingDevice1CsvQueue.is_set():
                self.powermeter.updatingDevice1CsvQueue.set()

            if not self.powermeter.updatingDevice2CsvQueue.is_set():
                self.powermeter.updatingDevice2CsvQueue.set()

            if self.polarimeter is not None:
                if not self.polarimeter.updatingCsvQueue.is_set():
                    self.polarimeter.updatingCsvQueue.set()

            if self.pyqt_process is not None and self.pyqt_process.is_alive():
                self.micrometerController.updatingPlotQueue.set()
                self.powermeter.updatingDevice1PlotQueue.set()
                self.powermeter.updatingDevice2PlotQueue.set()


            #POLARIMETER NEEDS TO START RUNNING BEFORE MOVES EXECUTE. IT DOESN'T CONSTANTLY RUN LIKE THE POWERMETER.
            if(self.polarimeter is not None):
                self.polarimeter.run = True
                self.__startPolarimeterThread()
            else:
                print("No polarimeter Connected")

        #WARNING: BECAUSE of comparing move.targethiehgt to micrometer position, can only have one decimal place micrometer movement
        # ALSO: won't recognize values like 0.1 and .1 as being the same. I'll fix this later.
        for i in range(self.numExecutions):
            for move in moveList:
                if not self.stopExecution and (self.micrometerController.micrometerPosition.decode('utf-8')[3:6].strip() != move.targetHeight):
                    move.execute()
                    print("Position:", self.micrometerController.micrometerPosition.decode('utf-8')[3:6].strip())
                elif (self.micrometerController.micrometerPosition.decode('utf-8')[3:6].strip() == move.targetHeight):
                    print("Can't move here, this is the current position.")
                else:
                    break

        self.executed.set()
        # time.sleep(2)

        self.micrometerController.updatingCsvQueue.clear()
        self.micrometerController.updatingPlotQueue.clear()
        self.powermeter.updatingDevice1CsvQueue.clear()
        self.powermeter.updatingDevice2CsvQueue.clear()
        self.powermeter.updatingDevice1PlotQueue.clear()
        self.powermeter.updatingDevice2PlotQueue.clear()
        if self.polarimeter is not None:
            self.polarimeter.dataAnalyzer.finishAnalyzeDataSignal.wait()
            self.polarimeter.dataAnalyzer.finishAnalyzeDataSignal.clear()
            self.polarimeter.updatingCsvQueue.clear()
        self.generateCsvs()
        print("DONE")

    def generateCsvs(self):
        micrometerArray = []
        powermeter1Array = []
        powermeter2Array = []
        while not self.micrometerController.csvQueue.empty():
            micrometerArray.append(self.micrometerController.csvQueue.get())

        while not self.powermeter.device1CsvQueue.empty():
            powermeter1Array.append(self.powermeter.device1CsvQueue.get())

        while not self.powermeter.device2CsvQueue.empty():
            powermeter2Array.append(self.powermeter.device2CsvQueue.get())

        if micrometerArray:
            with open("micrometertime.csv", mode="w", newline="") as f:
                writer = csv.writer(f)
                # Optionally, write a header row first:
                writer.writerow(["position (mm)", "time (seconds since jan 1 1975)"])
                # Each element of the tuple goes into its own CSV column
                for row_tuple in micrometerArray:
                    writer.writerow(row_tuple)


        if powermeter1Array:
            with open("power1time.csv", mode="w", newline="") as f:
                writer = csv.writer(f)
                # Optionally, write a header row first:
                writer.writerow(["power 1 (W)", "time (seconds since jan 1 1975)"])
                # Each element of the tuple goes into its own CSV column
                for row_tuple in powermeter1Array:
                    writer.writerow(row_tuple)

        if powermeter2Array:
            with open("power2time.csv", mode="w", newline="") as f:
                writer = csv.writer(f)
                # Optionally, write a header row first:
                writer.writerow(["power 2 (W)", "time (seconds since jan 1 1975)"])
                # Each element of the tuple goes into its own CSV column
                for row_tuple in powermeter2Array:
                    writer.writerow(row_tuple)
        

        # ──────────────────────────────────────────────────────────────
        # 1.  Read the first column of each CSV and convert to float
        # ──────────────────────────────────────────────────────────────
            powermeter1CalcArray, powermeter2CalcArray = [], []

            for file_name, target in [("power1time.csv", powermeter1CalcArray),
                                    ("power2time.csv", powermeter2CalcArray)]:
                with open(file_name, mode="r", newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row:               # skip blank lines
                            continue
                        try:
                            target.append(float(row[0]))
                        except ValueError:        # skip header / malformed
                            continue

            # Convert to NumPy for vector math

            pm1 = np.array(powermeter1CalcArray, dtype=float)
            pm2 = np.array(powermeter2CalcArray, dtype=float)

            min_len = min(pm1.size, pm2.size)
            pm1 = pm1[:min_len]
            pm2 = pm2[:min_len]

            # ──────────────────────────────────────────────────────────────
            # 2.  Compute power difference
            # ──────────────────────────────────────────────────────────────
            powerdifference = pm1 - pm2          # ΔP = P₁ – P₂

        if self.polarimeter is not None:
            if self.polarimeter.dataAnalyzer.phase is not None and self.polarimeter.dataAnalyzer.strain is not None:
                with open("polarimetertime.csv", mode="w", newline="") as f:
                    writer = csv.writer(f)
                    print(f"Phase: {self.polarimeter.dataAnalyzer.phase}")
                    print(f"Strain: {self.polarimeter.dataAnalyzer.strain}")
                    writer.writerow(["phase", "strain"])
                    for phase_val, strain_val in zip(self.polarimeter.dataAnalyzer.phase, self.polarimeter.dataAnalyzer.strain):
                        writer.writerow([phase_val, strain_val])
                    self.polarimeter.dataAnalyzer.strain = None
                    self.polarimeter.dataAnalyzer.phase = None


    """addmove adds the move to the movelist and then udpates the move gui adding the move"""
    def __addMove(self, frameMoveList):
        moveToAdd = move.Move(self.micrometerController)
        self.moveList.append(moveToAdd)
        self.moveGui.updateList(self.moveList)

    """updateplotsfromdata is really bad right not... try catches for updating every plot that's open will likely lead to 
    very many exceptions being raised. besides that: 
    1. tries to update micrometer plot, sets triedmicrometer if the except hits
    2. tries to update the power plots, sets flag if except
    3. does same for other power plots, has only one bool for both tho???????
    4. if executed bool is set in collect, it feeds in polarimeter data to polarimeter plot and generates the csv
    also colors the lines on polarimeter plot and power plots. Need to like somehow standardize all this
    also tries to constantly set powermeter value text gui 
    5. recursively runs this funciton every 10 ms.
    !! also why is this self.powerplot.generatecsvfromplot line here... this seems lazy and should be put somewhere else
    """
    """DEAL WITH PLOTTING TRY CATCH""" 
    def updatePlotsFromData(self):
        self.timeStamp = time.time()
        if (self.executed.is_set()): #right here all of the things that need to be done immediately after move(s) are done executing happen
            if self.polarimeter is not None:
                self.polarimeter.run = False
            else:
                print("polarimeter could not be told to stop running because no polarimeter detected.")

            if self.powerPlot is not None:
                self.powerPlot.generateCsvFromPlot("pow.csv")
            else:
                print("no power plot open")
            if self.pow1Plot is not None:
                self.pow1Plot.generateCsvFromPlot("pow1.csv")
            if self.pow2Plot is not None:
                self.pow2Plot.generateCsvFromPlot("pow2.csv")
            self.updatingPlots.clear() 
            self.signalAngleFinder.set()
            self.executed.clear()
            self.stopExecution = False




        if self.powermeter is not None:
            self.power1Text.set(str(self.powermeter.device1Data))
            self.power2Text.set(str(self.powermeter.device2Data))
        
        if self.polarimeter is not None:
            self.s1Text.set(str(self.polarimeter.s1.value))
            self.s2Text.set(str(self.polarimeter.s2.value))
            self.s3Text.set(str(self.polarimeter.s3.value))

            

        self.root.after(10, self.updatePlotsFromData)