# pyqt_plot_process.py
import sys
import time
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class GraphingProcess(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # self.queue = queue
        self.setWindowTitle("PyQtGraph Process")

        self.plot_widget = pg.PlotWidget()
        self.curve = self.plot_widget.plot([], [])
        self.x_data = []
        self.y_data = []

        # Timer to poll queue
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.check_queue)
        # self.timer.start(100)  # 10 Hz

        self.setCentralWidget(self.plot_widget)

    def check_queue(self):
        """Pull all items from the queue and update the plot."""
        while not self.queue.empty():
            try:
                x, y = self.queue.get_nowait()
            except:
                break
            self.x_data.append(x)
            self.y_data.append(y)

        self.curve.setData(self.x_data, self.y_data)

def run_pyqt_app():
    app = QtWidgets.QApplication(sys.argv)
    window = GraphingProcess()
    window.show()
    sys.exit(app.exec_())
