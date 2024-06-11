import dataAnalysisVmaster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import controllerGui
import polarimeterGui
#TODO: take out unnecessary imports


class Gui:
    def __init__(self):
        self.window = tk.Tk()
        self.window.config(background="red")
        self.window.title("Data GUI")
        self.window.geometry("800x500")
        self.contGui = controllerGui.ControllerGui()
        self.polGui = polarimeterGui.PolarimeterGui()

    def run(self):
        self.__topMenu()
        self.window.mainloop()
    
    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=1000, height=30)
        frameTopMenu.config(bg="blue")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)

        #buttons
        self.__quitButton(frameTopMenu)

        self.__browseDataFileButton(frameTopMenu)

        self.__openMicrometerMenuButton(frameTopMenu)
        
        self.__openPolarimeterMenuButton(frameTopMenu)

    
    def __quitButton(self, frameTopMenu):
        quitButton = tk.Button(frameTopMenu, text="Quit", command=lambda: [self.window.quit()]) 
        quitButton.pack(side='right') 

    def __browseDataFileButton(self, frameTopMenu):
        browseDataFileButton = tk.Button(frameTopMenu, text="browse for data file", command=lambda: [self.__browseFile(self.window)])
        browseDataFileButton.pack(side='left')

    def __openMicrometerMenuButton(self, frameTopMenu):
        openMicrometerMenu = tk.Button(frameTopMenu, text="micrometer menu", command=lambda: [self.contGui.run()])
        openMicrometerMenu.pack(side="left")

    def __openPolarimeterMenuButton(self, frameTopMenu):
        openPolarimeterMenu = tk.Button(frameTopMenu, text="polarimeter menu", command=lambda: [self.polGui.run()])
        openPolarimeterMenu.pack(side="left")

    # browse file button helper method
    def __browseFile(self):
        self.filePath = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if(self.filePath):
            self.__plot()

    def __plot(self):
        timeList, strain, phase, s1List, s2List, s3List = dataAnalysisVmaster.analyzeData(self.filePath)
    
        # Write the analyzed data into a .csv file
        data = np.vstack((timeList, strain, phase)).T
        filename = 'analyzed_data.csv'
        np.savetxt(filename, data, delimiter=',', header='time (s),strain (mm/mm),phase (pi radians)', comments='')

        #setup tkinter frame for graphs
        frameGraphs = tk.Frame(self.window, width=800, height=400)
        frameGraphs.pack()
        frameGraphs.pack_propagate(False)

        # Plot phase vs. strain
        fig2, ax2 = plt.subplots()
        fig2.set_figheight(4)
        fig2.set_figwidth(4)
        ax2.plot(strain, phase)
        ax2.set_title('Phase vs. Strain')
        ax2.set_xlabel('Strain (mm/mm)')
        ax2.set_ylabel('Phase (pi radians)')
        
    
        # Embed the Matplotlib graph in Tkinter
        canvas1 = FigureCanvasTkAgg(fig2, master=frameGraphs)
        canvas1.get_tk_widget().pack(side="left")

        # Plot circle trace on sphere (for reference)
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


        # Embed the Matplotlib graph in Tkinter
        canvas1 = FigureCanvasTkAgg(fig3, master=frameGraphs)
        canvas1Widget = canvas1.get_tk_widget()
        canvas1.get_tk_widget().pack(side="left")