import move
import tkinter as tk

class MoveGui:
    

    def __init__(self, frameMoveList):
        self.root = frameMoveList
        self.moveFrame = tk.Frame(self.root, width=500, height=100)
        frameMoveList.config(bg="grey")
        frameMoveList.pack(side="top")
        frameMoveList.pack_propagate(False)
        self.move = move.Move()

    def run(self):
        
        self.mainloop()

     
            
