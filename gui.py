import dataAnalysisVmaster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import controller
import polarimeterGui
import powermeterGui
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

class Gui:
    def __init__(self):
        self.window = ThemedTk(theme="breeze")
        self.root = tk._default_root #same as window!
        self.window.title("Data GUI")
        self.window.geometry("1920x1080")
        self.numExecutions = 1
        self.micrometerController = controller.Controller()
        self.polGui = polarimeterGui.PolarimeterGui()
        self.powGui = powermeterGui.PowermeterGui()
        self.updatingPlots = True
        self.triedPowermeters = False
        self.triedMicrometer = False

        defualtMove = move.Move(self.micrometerController)
        self.moveList = [defualtMove]

        
        
        # Create main layout frames
        self.mainFrame = tk.Frame(self.window, background="green", width=100, height=800)
        self.mainFrame.grid(row=0, column=1, sticky="nsew")
        self.mainFrame.grid_propagate(False)

       
       

        
        self.listFrame = tk.Frame(self.window, background="light grey", width=500, height=500)  # Adjust the width here for the left panel
        self.listFrame.grid(row=0, column=0, sticky="nsew")
        self.listFrame.grid_propagate(False)

          # Create top menu frame
        self.topMenuFrame = tk.Frame(self.window, background="blue", height=30)  # Adjust the height here
        self.topMenuFrame.grid(row=0, column=0, columnspan=2, sticky="new")
        self.topMenuFrame.grid_propagate(False)
        self.addTopMenuButtons()
        
        self.window.columnconfigure(0, weight=1)  # Make the list frame column expandable
        self.window.columnconfigure(1, weight=3)  # Make the main frame column expandable
        self.window.rowconfigure(0, weight=1)     # Make the row expandable

        
        self.moveGui = moveGui.MoveGui(self.listFrame, self.moveList, 100, width=500)
        self.addMoveListButtons(self.listFrame)
        
        self.micrometerController.goHome()
        
        self.micrometerPlot = Plot2D('micrometer plot', 'time', 'distance')
        self.powerPlot = Plot2D('power plot', 'distance (no idea)', 'power (um)')
        self.root.after(100, self.updatePlotsFromData)

    def run(self):
        self.window.mainloop()

    def addTopMenuButtons(self):
        self.__quitButton(self.topMenuFrame)
        # self.__browseDataFileButton(self.topMenuFrame)
        # self.__openMicrometerMenuButton(self.topMenuFrame)
        # self.__openPolarimeterMenuButton(self.topMenuFrame)
        # self.__openPowermeterMenuButton(self.topMenuFrame)

    def addMoveListButtons(self, listFrame):
        listFrame.grid_rowconfigure(0, weight=1)
        listFrame.grid_rowconfigure(1, weight=0)
        listFrame.grid_columnconfigure(1, weight=0)
        listFrame.grid_columnconfigure(2, weight=1)
        executeAllMovesButton = ttk.Button(listFrame, text='execute all moves', command=lambda: self.__startExecuteThread())
        executeAllMovesButton.grid(row=2, column=0, sticky='sw', pady=5, padx=30)
        addMoveButton = ttk.Button(listFrame, text='add move', command=lambda: self.__addMove(listFrame))
        addMoveButton.grid(row=1, column=0, sticky='sw', pady=5, padx= 30)
        
        

        ttk.Entry(listFrame, textvariable=self.numExecutions).grid(row=2, column=1, sticky='sw', pady=5)
        timesText = ttk.Label(listFrame, text='times').grid(row=2, column=2, sticky= 'w', pady=5, padx=30)

        


    def saveNumExecutionsInput(self, index, text_data):
        inputTxt = self.textInput.get("1.0", tk.END).strip()
        try:
            self.numExecutions = int(inputTxt)
            print(f"Saved number of executions: {self.numExecutions}")
        except ValueError:
            print("Invalid input, please enter a valid number")

    def __startExecuteThread(self):
        self.powerPlot.resetPlot()
        self.micrometerPlot.resetPlot()
        thread = Thread(target=self.__executeAllMoves, args=[])
        thread.start()

    def __executeAllMoves(self):
        for i in range(self.numExecutions):
            for move in self.moveList:
                move.move.execute()
        self.powerPlot.generateCsvFromPlot()

    def __quitButton(self, frameTopMenu):
        quitButton = tk.Button(frameTopMenu, text="Quit", command=lambda: [self.window.quit()])
        quitButton.pack(side='right')

        
    def __addMove(self, frameMoveList):
        moveToAdd = move.Move(self.micrometerController)
        self.moveList.append(moveToAdd)
        self.moveGui.updateList(self.moveList)

    def __browseDataFileButton(self, frameTopMenu):
        browseDataFileButton = tk.Button(frameTopMenu, text="browse for data file", command=lambda: [self.__browseFile(self.window)])
        browseDataFileButton.pack(side='left')

    def __openMicrometerMenuButton(self, frameTopMenu):
        openMicrometerMenu = tk.Button(frameTopMenu, text="micrometer menu", command=lambda: [self.contGui.run()])
        openMicrometerMenu.pack(side="left")

    def __openPolarimeterMenuButton(self, frameTopMenu):
        openPolarimeterMenu = tk.Button(frameTopMenu, text="polarimeter menu", command=lambda: [self.polGui.run()])
        openPolarimeterMenu.pack(side="left")

    def __openPowermeterMenuButton(self, frameTopMenu):
        openPowermeterMenu = tk.Button(frameTopMenu, text="powermeter menu", command=lambda: [self.powGui.run()])
        openPowermeterMenu.pack(side="left")

    def __browseFile(self):
        self.filePath = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if self.filePath:
            self.__plot()

    def __plot(self):
        timeList, strain, phase, s1List, s2List, s3List = dataAnalysisVmaster.analyzeData(self.filePath)
        data = np.vstack((timeList, strain, phase)).T
        filename = 'analyzed_data.csv'
        np.savetxt(filename, data, delimiter=',', header='time (s),strain (mm/mm),phase (pi radians)', comments='')
        frameGraphs = tk.Frame(self.window, width=800, height=400)
        frameGraphs.pack()
        frameGraphs.pack_propagate(False)
        fig2, ax2 = plt.subplots()
        fig2.set_figheight(4)
        fig2.set_figwidth(4)
        ax2.plot(strain, phase)
        ax2.set_title('Phase vs. Strain')
        ax2.set_xlabel('Strain (mm/mm)')
        ax2.set_ylabel('Phase (pi radians)')
        canvas1 = FigureCanvasTkAgg(fig2, master=frameGraphs)
        canvas1.get_tk_widget().pack(side="left")
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
        canvas1 = FigureCanvasTkAgg(fig3, master=frameGraphs)
        canvas1.get_tk_widget().pack(side="left")

    def updatePlotsFromData(self):
        self.timeStamp = time.time()
        if not self.triedMicrometer:
            try:
                self.micrometerPlot.updatePlot(self.timeStamp, self.micrometerController.micrometerPosition)
            except:
                print("micrometer not found")
                self.triedMicrometer = True
        if not self.triedPowermeters:
            try:
                self.powerPlot.updatePlot(self.micrometerController.micrometerPosition, abs(self.powGui.power.device1Data - self.powGui.power.device2Data))
            except:
                print("not enough powermeters connected.")
                self.triedPowermeters = True
        if self.updatingPlots:
            self.root.after(100, self.updatePlotsFromData)