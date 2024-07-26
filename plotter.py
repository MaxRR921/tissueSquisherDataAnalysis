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
        
        for i in range(len(x) - 1):
            if x[i + 1] < x[i]:
                self.ax.plot(x[i:i + 2], y[i:i + 2], color='blue')
            else:
                self.ax.plot(x[i:i + 2], y[i:i + 2], color='red')

        legend_elements = [
            Line2D([0], [0], color='red', lw=2, label='Unloading'),
            Line2D([0], [0], color='blue', lw=2, label='Loading')
        ]
        self.ax.legend(handles=legend_elements)


    def updatePolPlot(self, x, y):
           # Ensure data is in the correct format
        print("updatePolPlot called")
        x = np.char.decode(x)
        x = np.char.replace(x, '1TP', '')
        x = np.char.strip(x)
        x = x.astype(float)
        downward = False
        downward = np.any(np.diff(x) < 0)
        print(x)
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            if x.ndim == 1 and y.ndim == 1 and x.size == y.size:
                print("Data is correctly formatted")
                self.ax.clear()
                self.ax.plot(x, y, color=self.color)
                self.ax.set_xlabel(self.xAxisTitle)
                self.ax.set_ylabel(self.yAxisTitle)
                self.ax.set_title(self.title)
                self.ax.relim()
                self.ax.autoscale_view()
                try:
                    self.canvas.draw()
                except Exception as e:
                    print(f"Error in updatePolPlot canvas.draw(): {e}")
            else:
                print("Error: x and y arrays must be 1-dimensional and of the same length.")
        else:
            print("Error: x and y must be numpy arrays.")
    def generateCsvFromPlot(self):
        # Ensure that the data is in the format of lists of equal length
        keys = self.data.keys()
        values = zip(*self.data.values())

        with open("profiles1.csv", "w", newline="") as f:
            w = csv.writer(f)
            # Write the header
            w.writerow(keys)
            # Write the rows
            for row in values:
                w.writerow(row)
        