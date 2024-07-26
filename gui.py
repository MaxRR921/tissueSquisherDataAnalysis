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
        self.window = ThemedTk(theme="breeze")
        self.root = tk._default_root #same as window!
        self.window.title("Data GUI")
        self.window.geometry("800x800")
        self.numExecutions = 1
        self.micrometerController = controller.Controller()
        self.polarimeter = polarimeter.Polarimeter(self.micrometerController)
        self.powermeter = powermeter.Powermeter()
        self.updatingPlots = True
        self.triedPowermeters = False
        self.triedMicrometer = False
        self.phase = np.array(np.zeros)
        self.strain = np.array(np.zeros)
        self.executed = False
        self.startedPolarimeter = False
        self.power1Text = tk.StringVar()
        self.power2Text = tk.StringVar()
        self.power1Text.set("p1 no reading")
        self.power2Text.set("p2 no reading") 

        defualtMove = move.Move(self.micrometerController)
        self.moveList = [defualtMove]

        #plots:
        self.polPlot = None
        self.powerPlot = None
        self.micrometerPlot = None
        
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

        self.window.columnconfigure(0, weight=1)  # Make the list frame column expandable
        self.window.columnconfigure(1, weight=3)  # Make the main frame column expandable
        self.window.rowconfigure(0, weight=1)     # Make the row expandable
        self.window.rowconfigure(1, weight=2)

        #create the move list gui elements
        self.moveGui = moveGui.MoveGui(self.listFrame, self.moveList, 100, width=500)
        
        #micrometer moves to original position
        self.micrometerController.goHome()
        
        self.root.after(100, self.updatePlotsFromData)

    def run(self):
        self.window.mainloop()

    def addTopMenuButtons(self):
        self.__quitButton(self.topMenuFrame)
        self.__dropdownButton(self.topMenuFrame)
        self.__polarimeterButton(self.topMenuFrame)
        self.__browseDataFileButton(self.topMenuFrame)

    #ALL BUTTONS IN TOP MENU

    def __browseDataFileButton(self, frameTopMenu):
        browseDataFileButton = ttk.Button(frameTopMenu, text="browse for data file", command=lambda: self.__browseFile())
        browseDataFileButton.pack(side='left')

    def __browseFile(self):
        self.filePath = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if self.filePath:
            self.__plot()

    def __quitButton(self, frameTopMenu):
        quitButton = ttk.Button(frameTopMenu, text='Quit', command=lambda: self.window.quit())
        quitButton.pack(side="right")

    def __polarimeterButton(self, frameTopMenu):
        polarimeterButton = ttk.Button(frameTopMenu, text='p', command=lambda: self.__startPolarimeterThread())
        polarimeterButton.pack(side="right")

    def __startPolarimeterThread(self):
        thread = Thread(target=self.polarimeter.start, args=[])
        thread.start()

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

    def __option2(self):
        print("Option 2 selected")
        self.powerPlot = Plot2D('power plot', 'distance (mm)', 'power (um)')

    def __option3(self):
        print("Option 3 selected")
        self.polPlot = Plot2D('polarimeter plot', 'strain', 'phase')


    def addBottomFrameButtons(self, listFrame):
        numExec = tk.StringVar()
        ttk.Entry(listFrame, textvariable=numExec).grid(row=2, column=1, sticky='sw', pady=5)
        listFrame.grid_rowconfigure(0, weight=1)
        listFrame.grid_rowconfigure(1, weight=0)
        listFrame.grid_columnconfigure(1, weight=0)
        listFrame.grid_columnconfigure(2, weight=1)
        listFrame.grid_columnconfigure(3, weight=2)
        
        executeAllMovesButton = ttk.Button(listFrame, text='execute all moves', command=lambda: self.__startExecuteThread())
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

    def __startExecuteThread(self):
        if self.polPlot is not None:
            self.polPlot.resetPlot()
        else:
            print("no polarimeter plot present")
        if self.powerPlot is not None:
            self.powerPlot.resetPlot()
        else:
            print("no power plot open")
        if self.micrometerPlot is not None:
            self.micrometerPlot.resetPlot()
        else:
            print("no micrometer plot open")
        thread = Thread(target=self.__collect, args=[])
        thread.start()

    def __collect(self):
        print("LETS GO")
        try:
            self.polarimeter.run = True
            self.__startPolarimeterThread()
        except:
            print("failed to start polarimeter thread.")

        for i in range(self.numExecutions):
            for move in self.moveList:
                move.execute()
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
            self.powerPlot.generateCsvFromPlot()
        else:
            print("no power plot open")
        self.executed = True
        print("DONE")


    
    def __addMove(self, frameMoveList):
        moveToAdd = move.Move(self.micrometerController)
        self.moveList.append(moveToAdd)
        self.moveGui.updateList(self.moveList)

   

    def __plot(self):
        analyzer = dataAnalysisVmaster.DataAnalyzer()
        timeList, strain, phase, s1List, s2List, s3List = analyzer.analyze_data(self.filePath)
        data = np.vstack((timeList, strain, phase)).T
        filename = 'analyzed_data.csv'
        np.savetxt(filename, data, delimiter=',', header='time (s),strain (mm/mm),phase (pi radians)', comments='')

        # Create a new frame for graphs
        frameGraphs = tk.Frame(self.window, width=800, height=400)
        frameGraphs.grid(row=2, column=0, columnspan=2, sticky="nsew")
        frameGraphs.grid_propagate(False)

        # Create the first plot
        fig2, ax2 = plt.subplots()
        fig2.set_figheight(4)
        fig2.set_figwidth(4)
        ax2.plot(strain, phase)
        ax2.set_title('Phase vs. Strain')
        ax2.set_xlabel('Strain (mm/mm)')
        ax2.set_ylabel('Phase (pi radians)')
        canvas1 = FigureCanvasTkAgg(fig2, master=frameGraphs)
        canvas1.get_tk_widget().grid(row=0, column=0)

        # Create the second plot
        fig3 = plt.figure()
        ax3 = fig3.add_subplot(111, projection='3d')
        fig3.set_figheight(4)
        fig3.set_figwidth(5)
        phi = np.linspace(0, np.pi, 100)
        theta = np.linspace(0, 2 * np.pi, 100)
        phi, theta = np.meshgrid(phi, theta)
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        ax3.plot_wireframe(x, y, z, color='r', alpha=0.5, linewidth=0.1)
        ax3.scatter(s1List, s2List, s3List)
        ax3.set_xlabel('s1')
        ax3.set_ylabel('s2')
        ax3.set_zlabel('s3')
        ax3.set_title('Circle Trace on Sphere')
        canvas2 = FigureCanvasTkAgg(fig3, master=frameGraphs)
        canvas2.get_tk_widget().grid(row=0, column=1)

        # Ensure the parent window is properly configured to handle the new frame
        self.window.rowconfigure(2, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)


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

            if self.polPlot is not None:
                self.polPlot.updatePlot(self.polarimeter.positionList, self.phase.tolist())
                self.executed = False
        try:
            self.power1Text.set(str(self.powermeter.device1Data))
            self.power2Text.set(str(self.powermeter.device2Data))
        except:
            print("error updating power text")


        if self.updatingPlots:
            self.root.after(100, self.updatePlotsFromData)




