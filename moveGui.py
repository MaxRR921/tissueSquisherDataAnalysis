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

    def run(self):
        
        self.mainloop()

     
            
