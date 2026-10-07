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
        self._moveSamples = []
        # (moveStart, moveEnd, firstReading, lastReading) epoch times for the last goToHeight, or None
        self.lastMoveTiming = None

    @property
    def currentPosition(self):
        return self.agiltron.currentPosition

    def goToHeight(self, pos):
        self._moveSamples = []
        startPos = self.agiltron.currentPosition
        self.agiltron.goToHeight(pos, on_step=self._pushSample)
        self.lastMoveTiming = self._computeTiming(startPos)

    def _computeTiming(self, startPos):
        """Movement start/end = first/last poll where the position changed from the previous reading.
        Resolution is one poll interval (~50 ms + serial round trip)."""
        if not self._moveSamples:
            return None
        changeTimes = []
        prev = startPos
        for t, p in self._moveSamples:
            if p != prev:
                changeTimes.append(t)
            prev = p
        moveStart = changeTimes[0] if changeTimes else None
        moveEnd = changeTimes[-1] if changeTimes else None
        return (moveStart, moveEnd, self._moveSamples[0][0], self._moveSamples[-1][0])

    def setVelocity(self, speed):
        self.agiltron.setVelocity(speed)

    def _pushSample(self, scaled_pos):
        now = time.time()
        self._moveSamples.append((now, scaled_pos))
        if self.updatingCsvQueue.is_set():
            self.csvQueue.put((scaled_pos, now))
        if self.updatingPlotQueue.is_set():
            self.plotQueue.put((now, scaled_pos))
