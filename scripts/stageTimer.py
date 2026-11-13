import time
from typing import NamedTuple, Optional


class MoveTiming(NamedTuple):
    """Epoch times for one goToHeight. moveStart/moveEnd are None if no position change was seen."""
    moveStart: Optional[float]
    moveEnd: Optional[float]
    firstReading: float
    lastReading: float

    @property
    def movingTime(self):
        """Seconds between the first and last detected position change, or None if nothing moved."""
        if self.moveStart is None or self.moveEnd is None:
            return None
        return self.moveEnd - self.moveStart

    @property
    def readingWindow(self):
        """Seconds between the first and last poll of the move (includes lead-in and the stability wait)."""
        return self.lastReading - self.firstReading

    def velocity(self, distance):
        """Average velocity over the moving time, or None if there's no usable moving time."""
        elapsed = self.movingTime
        if elapsed is None or elapsed <= 0:
            return None
        return distance / elapsed


class StageTimer:
    """Collects timestamped position samples during a move and reduces them to a MoveTiming."""

    def __init__(self):
        self._samples = []
        self._startPos = None

    def begin(self, startPos):
        self._samples = []
        self._startPos = startPos

    def sample(self, pos):
        """Record one poll and return its timestamp."""
        now = time.time()
        self._samples.append((now, pos))
        return now

    def finish(self):
        """Movement start/end = first/last poll where the position changed from the previous reading.
        Resolution is one poll interval (~50 ms + serial round trip). Returns None if nothing was polled."""
        if not self._samples:
            return None
        changeTimes = []
        prev = self._startPos
        for t, p in self._samples:
            if p != prev:
                changeTimes.append(t)
            prev = p
        moveStart = changeTimes[0] if changeTimes else None
        moveEnd = changeTimes[-1] if changeTimes else None
        return MoveTiming(moveStart, moveEnd, self._samples[0][0], self._samples[-1][0])
