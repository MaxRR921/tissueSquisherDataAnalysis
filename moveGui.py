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
     
        setVelocityLabel = tk.Label(self.moveFrame, text="set velocity")
        inputTxtVelocity = tk.Text(self.moveFrame, height = 1, width = 10) 
        inputTxtVelocity.pack(side="bottom")
        setVelocityLabel.pack(side="top")

        setHeightLabel = tk.Label(self.moveFrame, text="Set the target height")
        inputTxtHeight = tk.Text(self.moveFrame, height = 1, width = 10) 
        inputTxtHeight.pack(side="bottom")
        setHeightLabel.pack(side="top")

        setFrontDelayLabel = tk.Label(self.moveFrame, text="set front delay")
        inputTxtFrontDelay = tk.Text(self.moveFrame, height = 1, width = 10) 
        inputTxtFrontDelay.pack(side="bottom")
        setFrontDelayLabel.pack(side="top")

        setBackDelayLabel = tk.Label(self.moveFrame, text="set back delay")
        inputTxtBackDelay = tk.Text(self.moveFrame, height = 1, width = 10) 
        inputTxtBackDelay.pack(side="bottom")
        setBackDelayLabel.pack(side="top")

    
        
        saveButton = tk.Button(self.moveFrame, text="save", command=lambda: [self.move.saveInputs(inputTxtVelocity.get("1.0", "end-1c"), inputTxtHeight.get("1.0", "end-1c"), inputTxtFrontDelay.get("1.0", "end-1c"), inputTxtBackDelay.get("1.0", "end-1c") )])
        saveButton.pack(side="bottom")

