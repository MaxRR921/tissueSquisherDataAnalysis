import dataAnalysisVmaster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import controller
import powermeter
from plotter import Plot2D
import time
import move
import moveGui
from threading import Thread
import csv
from csv import writer
from csv import DictWriter
from tkinter import ttk
from ttkthemes import ThemedTk
import polarimeter



class Gui:
    def __init__(self):
        #initializing UI
        self.window = ThemedTk(theme="breeze")
        self.root = tk._default_root #same as window!
        self.window.title("Data GUI")
        self.window.geometry("800x800")
        self.numExecutions = 1

        #Initializing device classes.
        self.micrometerController = controller.Controller()
        self.polarimeter = polarimeter.Polarimeter(self.micrometerController)
        self.powermeter = powermeter.Powermeter()

        # Event booleans
        self.updatingPlots = False
        self.triedPowermeters = False
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

        #THREADS:
        self.polarimeterThread = Thread(target=self.polarimeter.start, args=[])
        self.powermeterThread = Thread(target=self.powermeter.start, args=[])
        self.executeThread = Thread(target=self.__collect, args=[])

        self.powermeterThread.start()

        #plots:
        self.plotList = []
        self.polPlot = None
        self.powerPlot = None
        self.micrometerPlot = None
        
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
        
        #micrometer moves to original position
        self.micrometerController.goHome()
       
        #updating all plots 
        self.root.after(100, self.updatePlotsFromData)
        self.root.protocol('WM_DELETE_WINDOW', self.stop)

        self.stopExecution = False

        
        


    def stop(self):
        self.powermeter.stop()
        self.stopExecution = True
        try:
            self.executeThread.join()
        except:
            print("NOT currently executing")
        try:
            self.polarimeterThread.join() #needs to join so that it's not initializing when i tell it to stop...
        except:
            print("polarimeter thread not yet started")
        self.polarimeter.stop()
        self.micrometerController.stop()
        self.powermeterThread.join()

        self.root.destroy()

    def run(self):
        self.window.mainloop()

    def addTopMenuButtons(self):
        self.__dropdownButton(self.topMenuFrame)
        self.__browseDataFileButton(self.topMenuFrame)

    #ALL BUTTONS IN TOP MENU

    def __browseDataFileButton(self, frameTopMenu):
        browseDataFileButton = ttk.Button(frameTopMenu, text="browse for data file", command=lambda: self.__browseFile())
        browseDataFileButton.pack(side='left')

    def __browseFile(self):
        self.filePath = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if self.filePath:
            self.__plot()


    def __startPolarimeterThread(self):
        print("SHOULD START")
        self.polarimeterThread = Thread(target=self.polarimeter.start, args=[])
        self.polarimeterThread.start()

    def __dropdownButton(self, frameTopMenu):
        dropdownButton = ttk.Menubutton(frameTopMenu, text="Add Graphs", direction="below")
        dropdownMenu = tk.Menu(dropdownButton, tearoff=False)
        dropdownMenu.add_command(label="Micrometer position vs. Time", command=self.__option1)
        dropdownMenu.add_command(label="Power difference vs. Time", command=self.__option2)
        dropdownMenu.add_command(label="Polarimter Δpol vs. Time ", command=self.__option3)
        dropdownButton["menu"] = dropdownMenu
        dropdownButton.pack(side="left")

        
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


    def addBottomFrameButtons(self, listFrame):
        numExec = tk.StringVar()
        ttk.Entry(listFrame, textvariable=numExec).grid(row=2, column=1, sticky='sw', pady=5)
        listFrame.grid_rowconfigure(0, weight=1)
        listFrame.grid_rowconfigure(1, weight=0)
        listFrame.grid_columnconfigure(1, weight=0)
        listFrame.grid_columnconfigure(2, weight=1)
        listFrame.grid_columnconfigure(3, weight=2)
        
        executeAllMovesButton = ttk.Button(listFrame, text='execute all moves', command=lambda: self.startExecuteThread(self.moveList))
        executeAllMovesButton.grid(row=2, column=0, sticky='sw', pady=5, padx=30)

        addMoveButton = ttk.Button(listFrame, text='add move', command=lambda: self.__addMove(listFrame))
        addMoveButton.grid(row=1, column=0, sticky='sw', pady=5, padx=30)

        saveNumExecutionsButton = ttk.Button(listFrame, text='save', command=lambda: self.saveNumExecutions(numExec))
        saveNumExecutionsButton.grid(row=2,column=2, sticky='sw', pady=5, padx=50)
        power1Text = ttk.Label(listFrame, textvariable=self.power1Text).grid(row=2, column=3, sticky = 'w', pady=5, padx=2)
        power1Text = ttk.Label(listFrame, textvariable=self.power2Text).grid(row=2, column=3, sticky = 'e', pady=5, padx=10)
        timesText = ttk.Label(listFrame, text='times').grid(row=2, column=2, sticky= 'w', pady=5, padx=5)

        
    def saveNumExecutions(self, numExec):
        try:
            self.numExecutions = int(numExec.get())
            print(f"Saved number of executions: {self.numExecutions}")
        except ValueError:
            print("Invalid input, please enter a valid number")

    def startExecuteThread(self, moveList):
        for plot in self.plotList:
            plot.resetPlot()
        self.executeThread = Thread(target=self.__collect, args=[moveList])
        self.executeThread.start()




    def __collect(self, moveList):
        print("LETS GO")
        if not self.updatingPlots:
            self.updatingPlots = True
            self.root.after(10, self.updatePlotsFromData)
        try:
            self.polarimeter.run = True
            self.__startPolarimeterThread()
        except:
            print("failed to start polarimeter thread.")

        for i in range(self.numExecutions):
            for move in moveList:
                if not self.stopExecution:
                    move.execute()
                else:
                    break
        try:
            self.polarimeter.run = False
        except:
            print("No polarimeter")
        self.strain, self.phase  = dataAnalysisVmaster.analyzeData(self.polarimeter.s1List, self.polarimeter.s2List, self.polarimeter.s3List, self.polarimeter.timeList)
        print("PHASE:")  
        print(self.phase)
        print("STRAIN")
        print(self.strain)
        print(len(self.phase))
        print(len(self.strain))
        if self.powerPlot is not None:
            self.powerPlot.generateCsvFromPlot("pow.csv")
        else:
            print("no power plot open")
       
        self.executed = True
        print("DONE")


    
    def __addMove(self, frameMoveList):
        moveToAdd = move.Move(self.micrometerController)
        self.moveList.append(moveToAdd)
        self.moveGui.updateList(self.moveList)


    def updatePlotsFromData(self):
        self.timeStamp = time.time()
        try:
            if(self.micrometerController.downward):
                self.micrometerPlot.updatePlot(self.timeStamp, self.micrometerController.micrometerPosition[3:].strip())
            else:
                self.micrometerPlot.updatePlot(self.timeStamp, self.micrometerController.micrometerPosition[3:].strip())
        except:
            # print("micrometer not found")
            self.triedMicrometer = True
        
        try:
            self.powerPlot.updatePlot(self.micrometerController.micrometerPosition[3:].strip(), abs(self.powermeter.device1Data - self.powermeter.device2Data))
        except:
            # print("not enough powermeters connected.")
            self.triedPowermeters = True

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
        try:
            self.power1Text.set(str(self.powermeter.device1Data))
            self.power2Text.set(str(self.powermeter.device2Data))
        except:
            print("error updating power text")


        if self.updatingPlots:
            print("UPDATING")
            self.root.after(10, self.updatePlotsFromData)




