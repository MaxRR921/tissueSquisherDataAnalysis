import time
import queue
import multiprocessing
import threading
import agiltronController


class StageQueue:
    """Queue handler wrapping agiltronController for movement with data collection.
    Replaces controller.py (Newport Conex-CC micrometer) as the interface the GUI
    and Move class interact with.
    """

    def __init__(self):
        self.agiltron = agiltronController.agiltronController()
        self.csvQueue = queue.Queue()
        self.plotQueue = multiprocessing.Queue()
        self.updatingCsvQueue = threading.Event()
        self.updatingCsvQueue.clear()
        self.updatingPlotQueue = threading.Event()
        self.updatingPlotQueue.clear()
        self.currentPosition = 0

    def start(self):
        """Initialize the agiltron connection. Returns True/False."""
        return self.agiltron.start(run_loop=False)

    def goToHeight(self, pos):
        """Move to target position (int 0-50) and poll position into queues."""
        self.agiltron.setPosition(pos)
        # Poll position until movement completes
        stable_count = 0
        last_pos = None
        while stable_count < 5:
            time.sleep(0.05)
            raw_pos = self.agiltron.getCurrentPos()
            # Convert raw 0-700000 back to 0-50 scale
            scaled_pos = self.agiltron.scale_int(raw_pos, 0, 700000, 0, 50)
            self.currentPosition = scaled_pos
            if self.updatingCsvQueue.is_set():
                self.csvQueue.put((scaled_pos, time.time()))
            if self.updatingPlotQueue.is_set():
                self.plotQueue.put((time.time(), scaled_pos))
            # Check if position has stabilized (movement complete)
            if last_pos is not None and raw_pos == last_pos:
                stable_count += 1
            else:
                stable_count = 0
            last_pos = raw_pos
        print(f"Movement complete. Position: {self.currentPosition}")

    def setVelocity(self, speed):
        """Set max velocity (int 0-100)."""
        self.agiltron.setMaxVelocity(speed)

    def goHome(self):
        """Move to position 0."""
        self.goToHeight(0)

    def stop(self):
        """Close the serial connection."""
        self.agiltron.closePort()
