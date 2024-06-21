import move
import tkinter as tk

class MoveGui:
    

    def __init__(self, frameMoveList, controller):
        self.micrometerController = controller
        self.root = frameMoveList
        self.moveFrame = tk.Frame(self.root, width=300, height=100)
        self.moveFrame.config(bg="grey")
        self.moveFrame.pack(side="top")
        self.moveFrame.pack_propagate(False)
        self.move = move.Move(self.micrometerController)
        self.__setMoveAttributesFrame()

    def run(self):
        
        self.mainloop()


    def __setMoveAttributesFrame(self):
        self.moveFrame.grid_columnconfigure(0, weight=1)
        self.moveFrame.grid_columnconfigure(1, weight=1)
        self.moveFrame.grid_columnconfigure(2, weight=1)
        self.moveFrame.grid_columnconfigure(3, weight=1)
        self.moveFrame.grid_columnconfigure(4, weight=1)
        self.moveFrame.grid_rowconfigure(0, weight=1)
        self.moveFrame.grid_rowconfigure(1, weight=1)

        setVelocityLabel = tk.Label(self.moveFrame, text="set velocity")
        inputTxtVelocity = tk.Text(self.moveFrame, height=1, width=10)
        setVelocityLabel.grid(row=0, column=0, padx=10, pady=5)
        inputTxtVelocity.grid(row=1, column=0, padx=10, pady=5)

        setHeightLabel = tk.Label(self.moveFrame, text="Set the target height")
        inputTxtHeight = tk.Text(self.moveFrame, height=1, width=10)
        setHeightLabel.grid(row=0, column=1, padx=10, pady=5)
        inputTxtHeight.grid(row=1, column=1, padx=10, pady=5)

        setFrontDelayLabel = tk.Label(self.moveFrame, text="set front delay")
        inputTxtFrontDelay = tk.Text(self.moveFrame, height=1, width=10)
        setFrontDelayLabel.grid(row=0, column=2, padx=10, pady=5)
        inputTxtFrontDelay.grid(row=1, column=2, padx=10, pady=5)

        setBackDelayLabel = tk.Label(self.moveFrame, text="set back delay")
        inputTxtBackDelay = tk.Text(self.moveFrame, height=1, width=10)
        setBackDelayLabel.grid(row=0, column=3, padx=10, pady=5)
        inputTxtBackDelay.grid(row=1, column=3, padx=10, pady=5)

        saveButton = tk.Button(self.moveFrame, text="Save", command=lambda: self.__saveInputs(
            inputTxtVelocity.get("1.0", "end-1c"),
            inputTxtHeight.get("1.0", "end-1c"),
            inputTxtFrontDelay.get("1.0", "end-1c"),
            inputTxtBackDelay.get("1.0", "end-1c")
        ))
        saveButton.grid(row=2, column=2, padx=10, pady=10)

        executeButton = tk.Button(self.moveFrame, text="Execute", command=self.execute)
        executeButton.grid(row=2, column=3, padx=10, pady=10)

    def __saveInputs(self, velocity, height, front_delay, back_delay):
        self.move.saveInputs(self, velocity, height, front_delay, back_delay)
        print(f"Velocity: {velocity}, Height: {height}, Front Delay: {front_delay}, Back Delay: {back_delay}")

    def execute(self):
        self.move.execute()
        print("Execute button pressed")

