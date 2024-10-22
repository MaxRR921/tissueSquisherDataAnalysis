import controller
import time
"""
Each move object has a velocity, height, delays and a reference to the controller object so that it can tell it to
do these moves

Execute actually tells the controller to go to the position with the velocity

saveinputs saves the textbox inputs into the variables in this class.

"""
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

    def saveInputs(self, velocity, height, frontWait, backWait):
        self.velocity = velocity
        self.targetHeight = height
        self.frontDelay = frontWait
        self.backDelay = backWait

    def toString(self):
        print(f"Velocity: {self.velocity}, Height: {self.targetHeight}, Front Delay: {self.frontDelay}, Back Delay: {self.backDelay}")

        
    