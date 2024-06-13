import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plotter import Plotter

class PlotterGUI:
    def __init__(self, parentFrame):
        self.plotter = Plotter()
        self.framePlot = tk.Frame(parentFrame, bg='white')
        self.framePlot.pack(fill=tk.BOTH, expand=True)

        self.canvas = FigureCanvasTkAgg(self.plotter.fig, master=self.framePlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def updatePlot(self, timestamp, height):
        self.plotter.plotHeight(timestamp, height)
        self.canvas.draw()
        
    def resetPlot(self):
        self.plotter.resetPlot()
        self.canvas.draw()
