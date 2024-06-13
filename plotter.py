import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Plotter:
    def __init__(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.resetPlot()

    def resetPlot(self):
        self.data = {'time': [], 'height': []}
        self.ax.clear()
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Height (μm)')
        self.ax.set_title('Micrometer Position')
        self.fig.tight_layout()

    def plotHeight(self, timestamp, height):
        self.data['time'].append(timestamp)
        self.data['height'].append(height)
        self.ax.clear()
        self.ax.plot(self.data['time'], self.data['height'])
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Height (μm)')
        self.ax.set_title('Micrometer Position')
        self.ax.relim()
        self.ax.autoscaleView()
