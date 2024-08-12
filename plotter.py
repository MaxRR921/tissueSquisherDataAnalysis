import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import numpy as np
from matplotlib.lines import Line2D


class Plot2D:
    def __init__(self, title='untitled', xAxisTitle='x', yAxisTitle='y'):
        #set up window
        self.color = 'blue'
        
        #initialize variables 
        self.title = title
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.update = False
        ######

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        

        self.window = tk.Tk()
        self.window.title("Graph")
        self.window.geometry("400x400")
        self.framePlot = tk.Frame(self.window, bg='white')
        self.framePlot.pack(fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.framePlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.lastX = 0.0
        self.resetPlot()




    def resetPlot(self):
        self.data = {'xAxis': [], 'yAxis': []}
        
        self.ax.clear()
        self.ax.set_xlabel(self.xAxisTitle)
        self.ax.set_ylabel(self.yAxisTitle)
        self.ax.set_title(self.title)
       
        self.fig.tight_layout()
        self.canvas.draw()
        

    def updatePlot(self, xData, yData):
        if not isinstance(xData, list):           
            xData = float(xData)
            self.data['xAxis'].append(xData)
        else:
            xData = [float(i) for i in xData]
            self.data['xAxis'].extend(xData)
            
        if not isinstance(yData, list):
            yData = float(yData)
            self.data['yAxis'].append(yData)
        else:
            yData = [float(i) for i in yData]
            self.data['yAxis'].extend(yData)


        self.ax.clear()
        self.plotData()
        self.ax.set_xlabel(self.xAxisTitle)
        self.ax.set_ylabel(self.yAxisTitle)
        self.ax.set_title(self.title)
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()


    def plotData(self):
        x = np.array(self.data['xAxis'])
        y = np.array(self.data['yAxis'])
        print(self.title)
        print("x", x)
        print("y", y)
        self.ax.plot(x, y)
        legend_elements = [
            Line2D([0], [0], color='red', lw=2, label='Unloading'),
            Line2D([0], [0], color='blue', lw=2, label='Loading')
        ]
        self.ax.legend(handles=legend_elements)


    def colorLines(self):
        x = np.array(self.data['xAxis'])
        y = np.array(self.data['yAxis'])
        print("colorLines runs")
        for i in range(len(x) - 1):
            if x[i + 1] < x[i]:
                self.ax.plot(x[i:i + 2], y[i:i + 2], color='blue')
            else:
                self.ax.plot(x[i:i + 2], y[i:i + 2], color='red')


        self.ax.set_xlabel(self.xAxisTitle)
        self.ax.set_ylabel(self.yAxisTitle)
        self.ax.set_title(self.title)
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()


    def generateCsvFromPlot(self, name):
        # Ensure that the data is in the format of lists of equal length
        keys = self.data.keys()
        print("DATA:", self.data["xAxis"])
        values = zip(*self.data.values())

        with open(name, "w", newline="") as f:
            w = csv.writer(f)
            # Write the header
            w.writerow(keys)
            # Write the rows
            for row in values:
                w.writerow(row)
        