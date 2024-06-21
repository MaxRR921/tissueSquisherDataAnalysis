import controller
import time

class Move:

    def __init__(self, controller):
        self.velocity = 0.0
        self.targetHeight = 0.0
        self.frontDelay = 0.0
        self.backDelay = 0.0
        self.controller = controller

    def execute(self):
        self.controller.setVelocity(self.velocity)
        time.sleep(self.frontDelay)
        self.controller.goToHeight(self.targetHeight)
        time.sleep(self.backDelay)

    