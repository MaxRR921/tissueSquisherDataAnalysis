import time
import queue
import multiprocessing
import threading


class StageQueue:
    """Queue observer wrapped around an agiltronController instance. Pushes position
    samples into csvQueue/plotQueue during moves; all hardware ops live on agiltron."""

    def __init__(self, agiltron):
        self.agiltron = agiltron
        self.csvQueue = queue.Queue()
        self.plotQueue = multiprocessing.Queue()
        self.updatingCsvQueue = threading.Event()
        self.updatingCsvQueue.clear()
        self.updatingPlotQueue = threading.Event()
        self.updatingPlotQueue.clear()

    @property
    def currentPosition(self):
        return self.agiltron.currentPosition

    def goToHeight(self, pos):
        self.agiltron.goToHeight(pos, on_step=self._pushSample)

    def setVelocity(self, speed):
        self.agiltron.setVelocity(speed)

    def _pushSample(self, scaled_pos):
        now = time.time()
        if self.updatingCsvQueue.is_set():
            self.csvQueue.put((scaled_pos, now))
        if self.updatingPlotQueue.is_set():
            self.plotQueue.put((now, scaled_pos))
