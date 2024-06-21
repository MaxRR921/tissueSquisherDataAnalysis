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
        self.__setHeightFrame()

    def run(self):
        
        self.mainloop()

     
    def __setHeightFrame(self):
     
        heightFrame = tk.Frame(self.moveFrame, width=100, height=100)
        heightFrame.config(bg="green")
        heightFrame.pack(side="left")
        heightFrame.pack_propagate(False)

        setHeightLabel = tk.Label(heightFrame, text="Set the height")
        inputtxt = tk.Text(heightFrame, height = 1, width = 10) 
        
        setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [self.micrometerController.goToHeight(inputtxt.get("1.0", "end-1c"))])
        setHeightButton.pack(side="bottom")
        inputtxt.pack(side="bottom")
        setHeightLabel.pack(side="top")
