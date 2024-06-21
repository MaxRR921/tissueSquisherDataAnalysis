import move
import tkinter as tk

class moveGui:
    

    def __init__(self):
        
        self.move = move.Move()

    def run(self):
        
        self.mainloop()

    def __topMenu(self):
        frameTopMenu = tk.Frame(self.window, width=1000, height=30)
        frameTopMenu.config(bg="blue")
        frameTopMenu.pack(side='top')
        frameTopMenu.pack_propagate(False)

        #buttons
        self.__quitButton(frameTopMenu)

    def __quitButton(self, frameTopMenu):
        quitButton = tk.Button(frameTopMenu, text="Quit", command=lambda: [self.window.quit()]) 
        quitButton.pack(side='right') 
            
