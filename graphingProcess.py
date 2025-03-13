# pyqt_plot_process.py
import sys
import time
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class GraphingProcess(QtWidgets.QMainWindow):
    def __init__(self, updatingPlots, micrometerQueue):
        super().__init__()
        self.setWindowTitle("Multiple Subplots in a 2x2 Grid")

        self.micrometerQueue = micrometerQueue
        self.updatingPlots = updatingPlots
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

        self.setCentralWidget(self.plot_widget)

    def check_queue(self):
        """Pull all items from the queue and update the plot."""
        while not self.queue.empty():
            try:
                (x, y)= self.micrometerQueue.get_nowait()
            except:
                break
            self.x_data1.append(x)
            self.y_data1.append(y)

        self.curve.setData(self.x_data, self.y_data)

def run_pyqt_app(updatingPlots, micrometerQueue):
    app = QtWidgets.QApplication(sys.argv)
    window = GraphingProcess(updatingPlots, micrometerQueue)
    window.show()
    sys.exit(app.exec_())
