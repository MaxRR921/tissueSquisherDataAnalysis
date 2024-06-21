import move
import tkinter as tk

class MoveGui:
    

    def __init__(self, frameMoveList, controller):
        self.micrometerController = controller
        self.root = frameMoveList
        self.moveFrame = tk.Frame(self.root, width=1, height=1)
        frameMoveList.config(bg="grey")
        frameMoveList.pack(side="top")
        frameMoveList.pack_propagate(False)
        self.move = move.Move(self.micrometerController)

    def run(self):
        
        self.mainloop()

     
            
