import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import numpy as np
from matplotlib.lines import Line2D

"""plot2d defines a generic matplotlib plot in the format we want."""
class Plot2D:
    """init takes in a title for the x and y axes. It then initializes all of the plot things and then
    !CAlls reset plot which i feel shouldn't be necessary because I'm setting the title to the default plot titles, 
    then calling reset, whic sets it to the real title which seems really weird"""
    def __init__(self, title='untitled', xAxisTitle='x', yAxisTitle='y', showMinMax=False, on_close=None):
        #set up window
        self.color = 'blue'
        self.showMinMax = showMinMax
        #initialize variables 
        self.title = title
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.update = False

        self.on_close = on_close
        ######

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.maxValX = float(-10000000)
        self.minValX = float(100000000)
        self.maxValY = float(-10000000)
        self.minValY = float(10000000)

        self.window = tk.Toplevel()  # No master required
        self.window.title("Graph")
        self.window.geometry("400x400")

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.framePlot = tk.Frame(self.window, bg='white')
        self.framePlot.pack(fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.framePlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.lastX = 0.0
        self.resetPlot()


    """resetPlot clears the plot and its data"""
    def resetPlot(self):
        self.data = {'xAxis': [], 'yAxis': []}
        
        self.ax.clear()
        self.ax.set_xlabel(self.xAxisTitle)
        self.ax.set_ylabel(self.yAxisTitle)
        self.ax.set_title(self.title)

        self.maxValX = float(-10000000)
        self.minValX = float(100000000)
        self.maxValY = float(-10000000)
        self.minValY = float(10000000)
       
        self.fig.tight_layout()
        self.canvas.draw()

    """Handles window close event."""
    def _on_close(self):
        if self.on_close:
            self.on_close(self)
        self.window.destroy()
            
    """updatePlot !appends data to the plot's x and y data but the method isn't very standardized 
    because each type of plot's data will be in different  forms, so the checking of the data happens here
    I'm thinking the manipulation of the data to fit into the plots should happen in their respective classes instead this 
    print("PLOTS!!!")
    method runs from gui every 10 ms to make plots update in real time"""
    def updatePlot(self, xData, yData):
        if not isinstance(xData, list):           
            xData = float(xData)
            if(xData < self.minValX):
                self.minValX = xData
            elif(xData > self.maxValX):
                self.maxValX = xData
            self.data['xAxis'].append(xData)
        else:
            xData = [float(i) for i in xData]
            self.data['xAxis'].extend(xData)
            
        if not isinstance(yData, list):
            yData = float(yData)
            if(yData < self.minValY):
                self.minValY = yData
            elif(yData > self.maxValY):
                self.maxValY = yData
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

    """ plotdata plots all of the points for each plot al at once. !wondering if i can make it so it just 
    adds to the plot instead of replotting every single time and updating the legends and stuff. also this method seems
    weird to use with the polarimeter plot but that's a whole nother thing"""
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

        if self.showMinMax:
             # Display the pre-computed min and max values on the graph
            text_x = 0.7  # Position for text within the graph (adjust as needed)
            text_y_start = 0.95  # Starting position for the first text line
            self.ax.text(
                text_x, text_y_start,
                (
                    f"xMin: {self.minValX}\n"
                    f"xMax: {self.maxValX}\n"
                    f"yMin: {self.minValY}\n"
                    f"yMax: {self.maxValY}\n"
                    f"xdif: {self.maxValX - self.minValX}\n"
                    f"ydif: {self.maxValY - self.minValY}"
                ),
                transform=self.ax.transAxes,
                verticalalignment='top',
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.8)
            )

    """colorLines colors all of the lines based on the direction the x axis is moving. Colors red when the x axis is moving 
    in the positive direction, blue when moving in the negative direction."""
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

    """generateCsvFromPlot 
    it generates csvs from the cleaned up data of x and y axes that the plotter has."""
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


        