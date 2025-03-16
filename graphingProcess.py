# pyqt_plot_process.py
import sys
import time
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class GraphingProcess(QtWidgets.QMainWindow):
    def __init__(self, micrometerQueue, powermeter1Queue, powermeter2Queue):
        super().__init__()
        self.setWindowTitle("Multiple Subplots in a 2x2 Grid")

        self.micrometerQueue = micrometerQueue
        self.powermeter1Queue = powermeter1Queue
        self.powermeter2Queue = powermeter2Queue
        # Create a container widget and a QGridLayout
        container = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(container)

        # Subplot 1
        self.plot1 = pg.PlotWidget()
        self.plot1.setLabel('left', "Y Axis 1")
        self.plot1.setLabel('bottom', "X Axis 1")
        self.curve1 = self.plot1.plot([], [], pen='r')
        layout.addWidget(self.plot1, 0, 0)  # Row 0, Col 0

        # Subplot 2
        self.plot2 = pg.PlotWidget()
        self.plot2.setLabel('left', "Y Axis 2")
        self.plot2.setLabel('bottom', "X Axis 2")
        self.curve2 = self.plot2.plot([], [], pen='g')
        layout.addWidget(self.plot2, 0, 1)  # Row 0, Col 1

        # Subplot 3
        self.plot3 = pg.PlotWidget()
        self.plot3.setLabel('left', "Y Axis 3")
        self.plot3.setLabel('bottom', "X Axis 3")
        self.curve3 = self.plot3.plot([], [], pen='b')
        layout.addWidget(self.plot3, 1, 0)  # Row 1, Col 0

        # Subplot 4
        self.plot4 = pg.PlotWidget()
        self.plot4.setLabel('left', "Y Axis 4")
        self.plot4.setLabel('bottom', "X Axis 4")
        self.curve4 = self.plot4.plot([], [], pen='y')
        layout.addWidget(self.plot4, 1, 1)  # Row 1, Col 1

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
        # while not self.micrometerQueue.empty():
        #     x = time.time()
        #     y = self.micrometerQueue.get_nowait()
        #     print("ADDED")
        #     self.x_data1.append(x)
        #     self.y_data1.append(y)
        
        while not self.powermeter1Queue.empty() and not self.micrometerQueue.empty():
                self.x_data2.append(self.micrometerQueue.get_nowait())
                print(self.x_data2)
                self.y_data2.append(self.powermeter1Queue.get_nowait())
                print(self.y_data2)
                

        
        # self.curve1.setData(self.x_data1, self.y_data1)
        self.curve2.setData(self.x_data2, self.y_data2)

def run_pyqt_app(micrometerQueue, powermeter1Queue, powermeter2Queue):
    app = QtWidgets.QApplication(sys.argv)
    window = GraphingProcess(micrometerQueue, powermeter1Queue, powermeter2Queue)
    window.show()
    sys.exit(app.exec_())
