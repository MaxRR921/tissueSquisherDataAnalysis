import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Plot2D:
    def __init__(self, title='untitled', xAxisTitle='x', yAxisTitle='y'):
        #set up window
        
        
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
        
        
        try:
            self.data['xAxis'].append(xData)
            self.data['yAxis'].append(yData)
            self.ax.clear()
            self.ax.plot(self.data['xAxis'], self.data['yAxis'])
            self.ax.set_xlabel(self.xAxisTitle)
            self.ax.set_ylabel(self.yAxisTitle)
            self.ax.set_title(self.title)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        
        except:
            print("invalid data")