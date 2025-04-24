# pyqt_plot_process.py
import sys
import time
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from scipy.interpolate import interp1d

class GraphingProcess(QtWidgets.QMainWindow):
    def __init__(self, signalGraph, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue):
        super().__init__()
        self.setWindowTitle("Multiple Subplots in a 2x2 Grid")

        self.micrometerQueue = micrometerQueue
        self.powermeter1Queue = powermeter1Queue
        self.powermeter2Queue = powermeter2Queue
        self.phaseQueue = phaseQueue
        self.strainQueue = strainQueue
        self.signalGraph = signalGraph
        # Create a container widget and a QGridLayout
        container = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(container)

        # Subplot 1
        self.plot1 = pg.PlotWidget()
        self.plot1.setLabel('left', "Micrometer Position (mm)")
        self.plot1.setLabel('bottom', "Time")
        self.curve1 = self.plot1.plot([], [], pen='r')
        layout.addWidget(self.plot1, 0, 0)  # Row 0, Col 0

        # Subplot 2
        self.plot2 = pg.PlotWidget()
        self.plot2.setLabel('left', "Power 1 (W)")
        self.plot2.setLabel('bottom', "Time")
        self.curve2 = self.plot2.plot([], [], pen='g')
        layout.addWidget(self.plot2, 0, 1)  # Row 0, Col 1

        # Subplot 3
        self.plot3 = pg.PlotWidget()
        self.plot3.setLabel('left', "Power 2 (W)")
        self.plot3.setLabel('bottom', "Time")
        self.curve3 = self.plot3.plot([], [], pen='b')
        layout.addWidget(self.plot3, 1, 0)  # Row 1, Col 0

        # Subplot 4
        self.plot4 = pg.PlotWidget()
        self.plot4.setLabel('left', "Phase")
        self.plot4.setLabel('bottom', "Strain")
        self.curve4 = self.plot4.plot([], [], pen='y')
        layout.addWidget(self.plot4, 1, 1)  # Row 1, Col 1

        self.plot5 = pg.PlotWidget()
        self.plot5.setLabel('left', "Power Ratio (p1/p2)")
        self.plot5.setLabel('bottom', "Time")
        self.curve5 = self.plot5.plot([], [], pen='orange')
        layout.addWidget(self.plot5, 0, 2)  # Row 1, Col 1

        self.plot6 = pg.PlotWidget()
        self.plot6.setLabel('left', "Phase")
        self.plot6.setLabel('bottom', "Strain")
        self.curve6 = self.plot6.plot([], [], pen='y')
        layout.addWidget(self.plot6, 1, 2)  # Row 1, Col 1

        self.plot7 = pg.PlotWidget()
        self.plot7.setLabel('left', "Power Difference (W)")
        self.plot7.setLabel('bottom', "Time")
        self.curve7 = self.plot7.plot([], [], pen='orange')
        layout.addWidget(self.plot7, 1, 2)  # Row 1, Col 1
        # Put the container into the MainWindow
        self.setCentralWidget(container)

        # Data storage for each curve
        self.x_data1 = []
        self.y_data1 = []
        self.x_data2 = []
        self.y_data2 = []
        self.x_data3 = []
        self.y_data3 = []
        self.x_data4 = []
        self.y_data4 = []
        # Timer to poll queue
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_queue)
        self.timer.start(100)  # 10 Hz

   #NOTE: POWERMETER IS ACTUALLY POLLING QUITE SLOW.... so i made it update only when powermeter updates and the graph is way slower. 
    def check_queue(self):
        """Pull all items from the queue and update the plot."""
        diff = None
        while not self.signalGraph.empty():
            if self.signalGraph.get_nowait() == "STOP":
                self.plot1.clear()
                self.plot2.clear()
                self.plot3.clear()
                self.plot4.clear()
                self.plot5.clear()

                # Recreate the curve items
                self.curve1 = self.plot1.plot([], [], pen='r')
                self.curve2 = self.plot2.plot([], [], pen='g')
                self.curve3 = self.plot3.plot([], [], pen='b')
                self.curve4 = self.plot4.plot([], [], pen='m')
                self.curve5 = self.plot5.plot([], [], pen='y')
                self.curve6 = self.plot7.plot([],[], pen='w')

                # Clear data buffers
                self.x_data1.clear()
                self.y_data1.clear()
                self.x_data2.clear()
                self.y_data2.clear()
                self.x_data3.clear()
                self.y_data3.clear()
                self.x_data4.clear()
                self.y_data4.clear()


        while not self.micrometerQueue.empty():
            x, y = self.micrometerQueue.get_nowait()
            print("ADDED")
            self.x_data1.append(x)
            self.y_data1.append(y)
        
        while not self.powermeter1Queue.empty():
            x,y = self.powermeter1Queue.get_nowait()
            self.x_data2.append(x)
            self.y_data2.append(y)
                
        while not self.powermeter2Queue.empty():
            x,y = self.powermeter2Queue.get_nowait()
            self.x_data3.append(x)
            self.y_data3.append(y)

        if not self.phaseQueue == None and not self.strainQueue == None:
            while not self.phaseQueue.empty() and not self.strainQueue.empty():
                self.y_data4.append(self.phaseQueue.get_nowait())
                print("PLOT")
                self.x_data4.append(self.strainQueue.get_nowait())

            while not self.strainQueue.empty():
                x=self.strainQueue.get_nowait()
        
            while not self.phaseQueue.empty():
                y=self.phaseQueue.get_nowait()


        if  self.x_data3 and self.y_data3 and self.y_data2:
            interp_func = interp1d(self.x_data3, self.y_data3, kind='linear', fill_value='extrapolate')
            aligned_pow2 = interp_func(self.x_data2)
            diff = self.y_data2 / aligned_pow2

        if diff is not None:
            self.curve5.setData(self.x_data2, diff)
        
        if  self.x_data3 and self.y_data3 and self.y_data2:
            interp_func = interp1d(self.x_data3, self.y_data3, kind='linear', fill_value='extrapolate')
            aligned_pow2 = interp_func(self.x_data2)
            diff = self.y_data2 - aligned_pow2

        if diff is not None:
            self.curve6.setData(self.x_data2, diff)
        self.curve1.setData(self.x_data1, self.y_data1)
        self.curve2.setData(self.x_data2, self.y_data2)
        self.curve3.setData(self.x_data3, self.y_data3)
        self.curve4.setData(self.x_data4, self.y_data4)




def run_pyqt_app(signalGraph, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue):
    app = QtWidgets.QApplication(sys.argv)
    window = GraphingProcess(signalGraph, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue)
    window.show()
    sys.exit(app.exec_())
