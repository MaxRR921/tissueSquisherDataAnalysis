import dataAnalysisVmaster
import numpy as np
import tkinter as tk
import controller
import powermeter
from plotter import Plot2D
import time
import move
import moveGui
from threading import Thread
from tkinter import ttk
from ttkthemes import ThemedTk
import polarimeter

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

        try:
            self.polarimeter = polarimeter.Polarimeter(self.micrometerController)
            self.polarimeterThread = Thread(target=self.polarimeter.start, args=[])
        except:
            print("Polarimeter Connection Error")
            self.polarimeter = None

        try:
            self.powermeter = powermeter.Powermeter()
            self.powermeterThread = Thread(target=self.powermeter.start, args=[])
        except:
            print("Powermeter Connection Error. You need two powermeters connected at all times.")
            self.powermeter = None

        # Event booleans
        self.updatingPlots = True 
        self.triedMicrometer = False
        self.executed = False
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


        self.powermeterThread.start()

        #plots:
        self.plotList = []
        self.polPlot = None
        self.powerPlot = None
        self.micrometerPlot = None
        self.pow1Plot = None
        self.pow2Plot = None
        
        #list of times recorded
        self.timeList = []

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
        
       
        #updating all plots 
        self.root.protocol('WM_DELETE_WINDOW', self.stop)

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
        self.powermeter.stop()
        self.stopExecution = True
        self.updatingPlots = False
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

        self.root.destroy()

    """run begins the main loop. this is fine just a tkinter thing"""
    def run(self):
        self.window.mainloop()

    """addTopMenuButtons is executed from init, calls the methods that create all of the buttons"""
    def addTopMenuButtons(self):
        self.__dropdownButton(self.topMenuFrame)
        self.__browseDataFileButton(self.topMenuFrame)

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
        self.polarimeterThread = Thread(target=self.polarimeter.start, args=[])
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
        dropdownButton["menu"] = dropdownMenu
        dropdownButton.pack(side="left")

    """options are all of the options to select the plots you want to see displayed in real time (semi real time
    in the case of the polarimeter plot). iti initializes all of the plot2D objects """
    def __option1(self):
        print("Option 1 selected")
        self.micrometerPlot = Plot2D('micrometer plot', 'time', 'distance')
        self.plotList.append(self.micrometerPlot)

    def __option2(self):
        print("Option 2 selected")
        self.powerPlot = Plot2D('power plot', 'distance (mm)', 'power (um)')
        self.plotList.append(self.powerPlot)

    def __option3(self):
        print("Option 3 selected")
        self.polPlot = Plot2D('polarimeter plot', 'strain', 'phase')
        self.plotList.append(self.polPlot)

    def __option4(self):
        print("Option 3 selected")
        self.pow1Plot = Plot2D('power 1 plot', 'distance', 'power')
        self.plotList.append(self.pow1Plot)

    def __option5(self):
        print("Option 3 selected")
        self.pow2Plot = Plot2D('power 2 plot', 'distance', 'power')
        self.plotList.append(self.pow2Plot)

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

        addMoveButton = ttk.Button(listFrame, text='add move', command=lambda: self.__addMove(listFrame))
        addMoveButton.grid(row=1, column=0, sticky='sw', pady=5, padx=30)

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
        
            

    """startExecuteThread resets all of the constantly polling plots... starts the execute thread which calls 
    thecollect method. 
    !! should make it just use self.movelist...."""
    def startExecuteThread(self, moveList):
        for plot in self.plotList:
            plot.resetPlot()
        self.executeThread = Thread(target=self.__collect, args=[moveList])
        self.executeThread.start()



    """collect is a lot of logic. !should make it just use self.movelist
    if the plots currently aren't updating, it calls the recursive updatePlots function to update the plots 
    every 100 ms. Should just have this instead of having all plots update all of the time.
    then talls the polarimeter to start running, and starts its thread im thinking there is probably some cleaner logic
    for this. 
    !!in the for loop, it does every move the number of executions the user wants times. just calls move.execute 
     and if the program flags to stop execution of the move, it just breaks out of the loop a little haphazardly I 
      also should add a button for stopexecution. 
    !!! weird try catch for polarimeter.run i guess if the polarimeter is not there it shouldn't execute this.
    ! analyzes the polarimeter data right here, which seems kinda weird. I feel this should be within the polarimter class? or somewhere else just not here. 
    the function of this method should just be to collect data, not process it.
    !! also why is this self.powerplot.generatecsvfromplot line here... this seems lazy and should be put somewhere else
    !be aware of self.executed bool... should this even need to be here if all of the logic is sound?

     """
    def __collect(self, moveList):
        print("collecting data")
        if not self.updatingPlots:
            self.updatingPlots = True
            self.root.after(10, self.updatePlotsFromData)

        if(self.polarimeter is not None):
            self.polarimeter.run = True
            self.__startPolarimeterThread()
        else:
            print("No polarimeter Connected")

        for i in range(self.numExecutions):
            for move in moveList:
                if not self.stopExecution:
                    move.execute()
                else:
                    break

        if self.polarimeter is not None:
            self.polarimeter.run = False
        else:
            print("polarimeter could not be told to stop running because no polarimeter detected.")

        self.strain, self.phase  = dataAnalysisVmaster.analyzeData(self.polarimeter.s1List, self.polarimeter.s2List, self.polarimeter.s3List, self.polarimeter.timeList)

        if self.powerPlot is not None:
            self.powerPlot.generateCsvFromPlot("pow.csv")
        else:
            print("no power plot open")
       
        self.executed = True
        print("DONE")


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
    5. recursively runs this funciton every 10 ms."""
    def updatePlotsFromData(self):
        self.timeStamp = time.time()
        try:
            if(self.micrometerController.downward):
                self.micrometerPlot.updatePlot(self.timeStamp, self.micrometerController.micrometerPosition[3:].strip())
        except:
            print("micrometer not found")
        
        try:
            self.powerPlot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), abs(self.powermeter.device1Data - self.powermeter.device2Data))
        except:
            print("not enough powermeters connected.")

        try:
            self.pow1Plot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), self.powermeter.device1Data)

        except:
            print("not enough powermeters connected.")

        try:
            self.pow2Plot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), self.powermeter.device2Data)
        except:
            print("not enough powermeters connected.")

        if (self.executed == True):
            print("PHASE")
            print(self.phase)
            print("STRAIN")
            print(self.strain)
            self.updatingPlots = False
            if self.polPlot is not None:
                self.polPlot.updatePlot(self.polarimeter.positionList, self.phase.tolist())
                self.polPlot.colorLines()
                self.polPlot.generateCsvFromPlot("pol.csv")
            
            if self.powerPlot is not None:
                self.powerPlot.colorLines()
                
            self.executed = False
        if self.powermeter is not None:
            self.power1Text.set(str(self.powermeter.device1Data))
            self.power2Text.set(str(self.powermeter.device2Data))
        else: 
            print("error updating power text")


        if self.updatingPlots:
            print("UPDATING")
            self.root.after(10, self.updatePlotsFromData)




