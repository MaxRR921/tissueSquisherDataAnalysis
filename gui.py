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
        self.__dropdownButton(self.topMenuFrame)
        self.__browseDataFileButton(self.topMenuFrame)
        self.__startGraphingButton(self.topMenuFrame)
         

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

    """dropdownButton creates the dropdown button for all of the graphs that the user has the option to add"""
    def __dropdownButton(self, frameTopMenu):
        dropdownButton = ttk.Menubutton(frameTopMenu, text="Add Graphs", direction="below")
        dropdownMenu = tk.Menu(dropdownButton, tearoff=False)
        dropdownMenu.add_command(label="Micrometer position vs. Time", command=self.__option1)
        dropdownMenu.add_command(label="Power difference vs. Time", command=self.__option2)
        dropdownMenu.add_command(label="Polarimter Δpol vs. Time ", command=self.__option3)
        dropdownMenu.add_command(label="power1 vs. distance ", command=self.__option4)
        dropdownMenu.add_command(label="power2 vs. distance ", command=self.__option5)

        dropdownMenu.add_command(label="power dif vs. time", command=self.__option6)

        dropdownMenu.add_command(label="power 1 vs. time", command=self.__option7)

        dropdownMenu.add_command(label="power 2 vs. time", command=self.__option8)

        dropdownButton["menu"] = dropdownMenu
        dropdownButton.pack(side="left")

    def __startGraphingButton(self, frameTopMenu):
        startPyQtButton = ttk.Button(frameTopMenu, text='Start PyQt Plot', command=lambda: self.startPyqtProcess())
        startPyQtButton.pack(side="left")

    def startPyqtProcess(self):
        """Spawn a separate process that runs the PyQt/pyqtgraph event loop."""
        # If not already running (or if the process has ended), start it
        if self.pyqt_process is None or not self.pyqt_process.is_alive():
            print("Starting PyQt process...")
            if not self.polarimeter == None:
                self.pyqt_process = multiprocessing.Process(target=graphingProcess.run_pyqt_app,
                                                            args=(self.micrometerController.plotQueue, self.powermeter.device1PlotQueue, self.powermeter.device2PlotQueue, self.polarimeter.dataAnalyzer.phaseQueue, self.polarimeter.dataAnalyzer.strainQueue))
                self.pyqt_process.start()
            elif self.polarimeter == None:
                self.pyqt_process = multiprocessing.Process(target=graphingProcess.run_pyqt_app,
                                                            args=(self.micrometerController.plotQueue, self.powermeter.device1PlotQueue, self.powermeter.device2PlotQueue, None, None))
                self.pyqt_process.start()
        else:
            print("PyQt process is already running!")        

    """options are all of the options to select the plots you want to see displayed in real time (semi real time
    in the case of the polarimeter plot). iti initializes all of the plot2D objects""" 
    def __option1(self):
        print("Option 1 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.micrometerPlot = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.micrometerPlot = Plot2D('micrometer plot', 'time', 'distance', on_close=remove_plot)
        self.plotList.append(self.micrometerPlot)

    def __option2(self):
        print("Option 2 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.powerPlot = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.powerPlot = Plot2D('power plot', 'distance (mm)', 'power (um)', True, on_close=remove_plot)
        self.plotList.append(self.powerPlot)

    def __option3(self):
        print("Option 3 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.polPlot = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.polPlot = Plot2D('polarimeter plot', 'strain', 'phase', on_close=remove_plot)
        self.plotList.append(self.polPlot)

    def __option4(self):
        print("Option 4 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.pow1Plot = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.pow1Plot = Plot2D('power 1 plot', 'distance', 'power', on_close=remove_plot)
        self.plotList.append(self.pow1Plot)

    def __option5(self):
        print("Option 5 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.pow2Plot = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.pow2Plot = Plot2D('power 2 plot', 'distance', 'power', on_close=remove_plot)
        self.plotList.append(self.pow2Plot)

    def __option6(self):
        print("Option 6 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.noisePlotPowDif = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.noisePlotPowDif = Plot2D("power dif vs time", 'time', 'power dif', on_close=remove_plot)
        self.plotList.append(self.noisePlotPowDif)

    def __option7(self):
        print("Option 7 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.noisePlotPow1 = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.noisePlotPow1 = Plot2D("power 1 vs time", 'time', 'power dif', on_close=remove_plot)
        self.plotList.append(self.noisePlotPow1)

    def __option8(self):
        print("Option 8 selected")
        def remove_plot(plot):
            self.plotList.remove(plot)
            self.noisePlotPow2 = None  # Clear the reference
            print(f"Plot '{plot.title}' closed and removed from plotList.")
        
        self.noisePlotPow2 = Plot2D("power 2 vs time", 'time', 'power dif', on_close=remove_plot)
        self.plotList.append(self.noisePlotPow2)
            
            

    """adds all of the buttons in the bottom frame"""
    def addBottomFrameButtons(self, listFrame):
        numExec = tk.StringVar()
        ttk.Entry(listFrame, textvariable=numExec).grid(row=2, column=1, sticky='sw', pady=5)
        listFrame.grid_rowconfigure(0, weight=1)
        listFrame.grid_rowconfigure(1, weight=0)
        listFrame.grid_columnconfigure(1, weight=0)
        listFrame.grid_columnconfigure(2, weight=1)
        listFrame.grid_columnconfigure(3, weight=2)
        
        executeAllMovesButton = ttk.Button(listFrame, text='execute all moves', command=lambda: (self.saveNumExecutions(numExec), self.startExecuteThread(self.moveList)))
        executeAllMovesButton.grid(row=2, column=0, sticky='sw', pady=5, padx=30)

        recordNoiseButton = ttk.Button(listFrame, text='collect noise', command=lambda: (self.startNoiseThread()))
        recordNoiseButton.grid(row=2, column=3, sticky='sw', pady=5, padx=30)

        addMoveButton = ttk.Button(listFrame, text='add move', command=lambda: self.__addMove(listFrame))
        addMoveButton.grid(row=1, column=0, sticky='sw', pady=5, padx=30)

        stopExecutionButton = ttk.Button(listFrame, text='Stop Execution', command=lambda: setattr(self, 'stopExecution', True))
        stopExecutionButton.grid(row=1, column=1, sticky='sw', pady=5, padx=30)

        
        raiseMicrometerButton = ttk.Button(listFrame, text='Raise Micrometer', command=lambda: self.__raiseMicrometer())
        raiseMicrometerButton.grid(row=1, column=2, sticky='sw', pady=5, padx=30)

        if self.powermeter is not None:
            power1Text = ttk.Label(listFrame, textvariable=self.power1Text).grid(row=2, column=3, sticky = 'w', pady=5, padx=2)
            power1Text = ttk.Label(listFrame, textvariable=self.power2Text).grid(row=2, column=3, sticky = 'e', pady=5, padx=10)
            timesText = ttk.Label(listFrame, text='times').grid(row=2, column=2, sticky= 'w', pady=5, padx=5)

    """ saveNumExecutions is called when executeall is pressed, saves the number of executions the user entered
    in the little box at the bottom, checks for invalid input in the textbox."""
    def saveNumExecutions(self, numExec):
        try:
            self.numExecutions = int(numExec.get())
            print(f"Saved number of executions: {self.numExecutions}")
        except ValueError:
            print("Invalid input, please enter a valid number")

    def __raiseMicrometer(self):
        raiseMove = move.Move(self.micrometerController)
        raiseMove.velocity = "1"
        raiseMove.targetHeight = "12"
        listTemp = []
        listTemp.append(raiseMove)
        self.startExecuteThread(listTemp)


        

    """startExecuteThread resets all of the constantly polling plots... starts the execute thread which calls 
    thecollect method. 
    !! should make it just use self.movelist...."""
    def startExecuteThread(self, moveList):
        for plot in self.plotList:
            plot.resetPlot()
        self.executeThread = threading.Thread(target=self.__collect, args=[moveList])
        self.executeThread.start()

    def startNoiseThread(self):
        for plot in self.plotList:
            plot.resetPlot()
        self.noiseThread = threading.Thread(target=self.__collectNoise)
        self.noiseThread.start()

    def __collectNoise(self):
        t = 20
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

        try:
            self.noisePlotPow2.generateCsvFromPlot("power 2 vs. time.csv")
        except:
            print("plot not open")
        
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
    


    def __collect(self, moveList):
        print("collecting data")
        if not self.updatingPlots.is_set():
            self.updatingPlots.set() 

        if not self.micrometerController.updatingCsvQueue.is_set():
            self.micrometerController.updatingCsvQueue.set()
            
        if not self.powermeter.updatingDevice1CsvQueue.is_set():
            self.powermeter.updatingDevice1CsvQueue.set()
        
        if not self.powermeter.updatingDevice2CsvQueue.is_set():
            self.powermeter.updatingDevice2CsvQueue.set()

        if self.pyqt_process is not None or self.pyqt_process.is_alive():
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
        self.generateCsvs()
        self.updatingPlots.clear()
        self.micrometerController.updatingCsvQueue.clear()
        self.micrometerController.updatingPlotQueue.clear()
        self.powermeter.updatingDevice1CsvQueue.clear()
        self.powermeter.updatingDevice2CsvQueue.clear()
        self.powermeter.updatingDevice1PlotQueue.clear()
        self.powermeter.updatingDevice2PlotQueue.clear()
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

        with open("micrometertime.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["position (mm)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in micrometerArray:
                writer.writerow(row_tuple)

        with open("power1time.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["power 1 (W)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in powermeter1Array:
                writer.writerow(row_tuple)

        with open("power2time.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["power 2 (W)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in powermeter2Array:
                writer.writerow(row_tuple)
                

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
        if self.updatingPlots.is_set():
            if(self.micrometerPlot is not None):
                try:
                    if(self.micrometerController.downward):
                        self.micrometerPlot.updatePlot(self.timeStamp, self.micrometerController.micrometerPosition[3:].strip())
                except:
                    print("micrometer not found")
            if self.powerPlot is not None: 
                try:
                    self.powerPlot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), abs(self.powermeter.device1Data - self.powermeter.device2Data))
                except:
                    print("not enough powermeters connected.")
            if self.pow1Plot is not None:
                try:
                    self.pow1Plot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), self.powermeter.device1Data)

                except:
                    print("not enough powermeters connected.")
            if self.pow2Plot is not None:
                try:
                    self.pow2Plot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), self.powermeter.device2Data)
                except:
                    print("not enough powermeters connected.")
            if self.noisePlotPowDif is not None:  
                try:
                    self.noisePlotPowDif.updatePlot(time.time(), self.powermeter.device1Data - self.powermeter.device2Data)
                except:
                    print("noise not going")
            if self.noisePlotPow1 is not None:
                try:
                    self.noisePlotPow1.updatePlot(time.time(), self.powermeter.device1Data)
                except:
                    print("noise not going")
            if self.noisePlotPow2 is not None:
                try:
                    self.noisePlotPow2.updatePlot(time.time(), self.powermeter.device2Data)
                except:
                    print("noise not going")

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
            print("PHASE")
            print(self.phase)
            print("STRAIN")
            print(self.strain)
            self.updatingPlots.clear() 
            if self.polPlot is not None:
                self.polPlot.updatePlot(self.polarimeter.positionList, self.phase.tolist())
                self.polPlot.colorLines()
                self.polPlot.generateCsvFromPlot("pol.csv")
            
            if self.powerPlot is not None:
                self.powerPlot.colorLines()
            
                        

                
                
            self.executed.clear()
            self.stopExecution = False


            
        
        if self.powermeter is not None:
            self.power1Text.set(str(self.powermeter.device1Data))
            self.power2Text.set(str(self.powermeter.device2Data))
        self.root.after(10, self.updatePlotsFromData)

