# pyqt_plot_process.py
import sys
import time
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from scipy.interpolate import interp1d
import numpy as np
from experiment_settings import POWER_DIFFERENCE_TO_FORCE

class SecondsAxis(pg.AxisItem):
    """Bottom axis that ticks at whole seconds (0, 1, 2, ...), widening the step (2, 5, 10, ...) as the run gets longer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(False)

    def tickValues(self, minVal, maxVal, size):
        span = maxVal - minVal
        if span <= 0:
            return []
        step = 1
        while span / step > 10:
            step = next(m * 10 ** e for e in range(len(str(step)) + 1) for m in (1, 2, 5) if m * 10 ** e > step)
        first = int(np.ceil(minVal / step)) * step
        return [(step, list(range(first, int(maxVal) + 1, step)))]

    def tickStrings(self, values, scale, spacing):
        return [str(int(round(v))) for v in values]


class GraphingProcess(QtWidgets.QMainWindow):
    def __init__(self, signalGraph, signalZero, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue):
        super().__init__()
        self.setWindowTitle("Multiple Subplots in a 2x2 Grid")

        self.micrometerQueue = micrometerQueue
        self.powermeter1Queue = powermeter1Queue
        self.powermeter2Queue = powermeter2Queue
        self.phaseQueue = phaseQueue
        self.strainQueue = strainQueue
        self.signalGraph = signalGraph
        self.signalZero = signalZero
        self.initial = 0.0
        self.zero_time = None
        self.zero_position = None
        self.sample_height = None
        self.sample_width = None
        self.pending_zero = None
        self.t0 = None  # time.time() of first sample in the run; x-axes are seconds since this
        # Create a container widget and a QGridLayout
        container = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(container)

        # Subplot 1
        self.plot1 = pg.PlotWidget(axisItems={'bottom': SecondsAxis(orientation='bottom')})
        self.plot1.setLabel('left', "Micrometer Position (mm)")
        self.plot1.setLabel('bottom', "Time since start (s)")
        self.plot1.setYRange(0, 120, padding=0)
        self.curve1 = self.plot1.plot([], [], pen='r')
        layout.addWidget(self.plot1, 0, 0)  # Row 0, Col 0

        # Subplot 2
        self.plot2 = pg.PlotWidget(axisItems={'bottom': SecondsAxis(orientation='bottom')})
        self.plot2.setLabel('left', "Power 1 (W)")
        self.plot2.setLabel('bottom', "Time since start (s)")
        self.curve2 = self.plot2.plot([], [], pen='g')
        layout.addWidget(self.plot2, 0, 1)  # Row 0, Col 1

        # Subplot 3
        self.plot3 = pg.PlotWidget(axisItems={'bottom': SecondsAxis(orientation='bottom')})
        self.plot3.setLabel('left', "Power 2 (W)")
        self.plot3.setLabel('bottom', "Time since start (s)")
        self.curve3 = self.plot3.plot([], [], pen='b')
        layout.addWidget(self.plot3, 0, 2)  # Row 1, Col 0

        # Subplot 4
        self.plot4 = pg.PlotWidget()
        self.plot4.setLabel('left', "Zeroed Normalized Power Difference")
        self.plot4.setLabel('bottom', "Compressive Strain (ΔL/H)")
        self.curve4 = self.plot4.plot([], [], pen='y')
        layout.addWidget(self.plot4, 1, 1)

        self.plot5 = pg.PlotWidget()
        self.plot5.setLabel('left',  "force")
        self.plot5.setLabel('bottom', "Power difference Normalized")     # unitless or “ε” if you prefer
        self.curve5 = self.plot5.plot([], [], pen='orange')
        layout.addWidget(self.plot5, 1, 2)



        self.plot6 = pg.PlotWidget(axisItems={'bottom': SecondsAxis(orientation='bottom')})
        self.plot6.setLabel('left', "Power Difference (W)")
        self.plot6.setLabel('bottom', "Time since start (s)")
        self.curve6 = self.plot6.plot([], [], pen='orange')
        layout.addWidget(self.plot6, 1, 0)  # Row 1, Col 1
        # Put the container into the MainWindow
        self.setCentralWidget(container)

        # Data storage for each curve
        self.x_data1 = []
        self.y_data1 = []
        self.x_data2 = []
        self.y_data2 = []
        self.x_data3 = []
        self.y_data3 = []
        self.force = [] 
        self.diff = []
        self.sum = []
        # Timer to poll queue
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_queue)
        
        self.timer.start(100)  # 10 Hz

    def _elapsed(self, t):
        """Convert an absolute time.time() stamp to seconds since the first sample of the run."""
        if self.t0 is None:
            self.t0 = t
        return t - self.t0

    def _strain_at(self, times):
        """Interpolate measured stage position, anchored at the Zero Force press."""
        zero_elapsed = self.zero_time - self.t0
        stage_times = [zero_elapsed]
        positions = [self.zero_position]
        for t, pos in zip(self.x_data1, self.y_data1):
            if t > zero_elapsed:
                stage_times.append(t)
                positions.append(pos)
        return (np.interp(times, stage_times, positions) - self.zero_position) / self.sample_height

   #NOTE: POWERMETER IS ACTUALLY POLLING QUITE SLOW.... so i made it update only when powermeter updates and the graph is way slower. 
    def check_queue(self):
        """Pull all items from the queue and update the plot."""
        self.diff = None
                
        while not self.signalGraph.empty():
            if self.signalGraph.get_nowait() == "STOP":
                self.plot1.clear()
                self.plot2.clear()
                self.plot3.clear()
                self.plot4.clear()
                self.plot5.clear()
                self.plot6.clear()


                # Recreate the curve items
                self.curve1 = self.plot1.plot([], [], pen='r')
                self.curve2 = self.plot2.plot([], [], pen='g')
                self.curve3 = self.plot3.plot([], [], pen='b')
                self.curve4 = self.plot4.plot([], [], pen='m')
                self.curve5 = self.plot5.plot([], [], pen='y')
                self.curve6 = self.plot6.plot([],[], pen='w')

                # Clear data buffers
                self.x_data1.clear()
                self.y_data1.clear()
                self.x_data2.clear()
                self.y_data2.clear()
                self.x_data3.clear()
                self.y_data3.clear()
                self.t0 = None


        while not self.micrometerQueue.empty():
            x, y = self.micrometerQueue.get_nowait()
            self.x_data1.append(self._elapsed(x))
            self.y_data1.append(y)

        if self.powermeter1Queue is not None:
            while not self.powermeter1Queue.empty():
                x,y = self.powermeter1Queue.get_nowait()
                self.x_data2.append(self._elapsed(x))
                self.y_data2.append(y)
                
        if self.powermeter2Queue is not None:
            while not self.powermeter2Queue.empty():
                x,y = self.powermeter2Queue.get_nowait()
                self.x_data3.append(self._elapsed(x))
                self.y_data3.append(y)

        if self.strainQueue is not None:
            while not self.strainQueue.empty():
                self.strainQueue.get_nowait()
        if self.phaseQueue is not None:
            while not self.phaseQueue.empty():
                self.phaseQueue.get_nowait()


       
        
        while not self.signalZero.empty():
            self.pending_zero = self.signalZero.get_nowait()

        if len(self.x_data3) >= 2 and self.y_data2:
            interp_func = interp1d(self.x_data3, self.y_data3, kind='linear', fill_value='extrapolate')
            aligned_pow2 = interp_func(self.x_data2)
            self.diff = self.y_data2 - aligned_pow2
            self.sum = self.y_data2 + aligned_pow2
            normalized = np.divide(self.diff, self.sum, out=np.full_like(self.sum, np.nan), where=self.sum != 0)

            if self.pending_zero is not None:
                command = self.pending_zero
                self.pending_zero = None
                if isinstance(command, tuple) and command[0] == "ZERO":
                    _, zero_time, position, height, width = command
                    elapsed = np.asarray(self.x_data2) + self.t0
                    before = np.flatnonzero((elapsed <= zero_time) & np.isfinite(normalized))
                    after = np.flatnonzero((elapsed > zero_time) & np.isfinite(normalized))
                    if len(before) or len(after):
                        index = before[-1] if len(before) else after[0]
                        self.initial = normalized[index]
                        self.zero_time = zero_time
                        self.zero_position = position
                        self.sample_height = height
                        self.sample_width = width  # Cube face area is width ** 2 if stress is added later.
                        self.curve4.clear()
                        self.curve5.clear()
                    else:
                        self.pending_zero = command

        if self.diff is not None and self.sum is not None:
            self.curve6.setData(self.x_data2, normalized)
            if self.zero_time is not None:
                times = np.asarray(self.x_data2)
                mask = times + self.t0 >= self.zero_time
                zeroed = normalized[mask] - self.initial
                self.curve4.setData(self._strain_at(times[mask]), zeroed)
                self.curve5.setData(times[mask], POWER_DIFFERENCE_TO_FORCE * zeroed)


        self.curve1.setData(self.x_data1, self.y_data1)
        self.curve2.setData(self.x_data2, self.y_data2)
        self.curve3.setData(self.x_data3, self.y_data3)




def run_pyqt_app(signalGraph, signalZero, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue):
    app = QtWidgets.QApplication(sys.argv)
    window = GraphingProcess(signalGraph, signalZero, micrometerQueue, powermeter1Queue, powermeter2Queue, phaseQueue, strainQueue)
    window.show()
    sys.exit(app.exec_())
