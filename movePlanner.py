import tkinter as tk

class MovePlanner:
    def __init__(self):
        self.moveQueue = []  # Initialize the move queue

    def openPlanningWindow(self, parent):
        self.planningWindow = tk.Toplevel(parent)
        self.planningWindow.title("Move Planning")

        heightLabel = tk.Label(self.planningWindow, text="Height:")
        heightLabel.pack()
        self.heightEntry = tk.Entry(self.planningWindow)
        self.heightEntry.pack()

        velocityLabel = tk.Label(self.planningWindow, text="Velocity:")
        velocityLabel.pack()
        self.velocityEntry = tk.Entry(self.planningWindow)
        self.velocityEntry.pack()

        delayLabel = tk.Label(self.planningWindow, text="Delay:")
        delayLabel.pack()
        self.delayEntry = tk.Entry(self.planningWindow)
        self.delayEntry.pack()

        addMoveButton = tk.Button(self.planningWindow, text="Add Move", command=self.addMove)
        addMoveButton.pack()

    def addMove(self):
        height = self.heightEntry.get()
        velocity = self.velocityEntry.get()
        delay = self.delayEntry.get()
        self.moveQueue.append({'height': height, 'velocity': velocity, 'delay': delay})

        self.heightEntry.delete(0, tk.END)
        self.velocityEntry.delete(0, tk.END)
        self.delayEntry.delete(0, tk.END)
