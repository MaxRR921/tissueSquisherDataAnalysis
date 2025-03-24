import tkinter as tk
from tkinter import ttk

class MoveGui(ttk.Frame):
    """
    init takes in the list of all moves, a height for the move gui elements and a width as well as the ttk.frame parent class
    it inherits from

    it sets up all of the ui elements and adds the existing moves (which should just be the default move. It takes in a reference
    to the top level gui so that it can start the execute thread from the execute button that is attached to each move.
    """
    def __init__(self, parent, gui, moveList, item_height, width):
        super().__init__(master=parent)
        self.pack(expand=True, fill='both', anchor="nw")
        self.gui = gui
        self.width = width
        # widget data
        self.moveList = moveList
        self.item_number = len(moveList)
        self.item_height = item_height

        # canvas 
        self.canvas = tk.Canvas(self, scrollregion=(0, 0, self.width, self.item_number * self.item_height))
        self.canvas.pack(side="right", expand=True, fill='both')

        # display frame
        self.frame = ttk.Frame(self.canvas, width=self.width)
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        

        self.populate_items()

        # scrollbar 
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="left", fill="y")

        # events
        self.canvas.bind_all('<MouseWheel>', self._on_mouse_wheel)
        self.bind('<Configure>', self.update_size)

    """event for scrolling using mouse wheel"""
    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")

    """updateList takes in a movelist and displays the moves based on this"""
    def updateList(self, moveList):
        self.moveList = moveList
        self.item_number = len(moveList)
        self.canvas.configure(scrollregion=(0, 0, self.width, self.item_number * self.item_height))

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.populate_items()
        self.update_size(None)

    """pupulate items creates all the items for the moves in movelist """
    def populate_items(self):
        for index, move in enumerate(self.moveList):
            self.create_item(move).pack(expand=True, fill='both', pady=4, padx=10)

    """update size updates the size of the frame size based on how many moves are given"""
    def update_size(self, event):
        canvas_width = self.winfo_width()
        canvas_height = self.item_number * self.item_height
        self.canvas.itemconfig(self.frame_id, width=canvas_width, height=canvas_height)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    """create_item creates a new move gui item based on the move it is fed"""
    def create_item(self, move):
        frame = ttk.Frame(self.frame)

        # grid layout
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

        # widgets 
        targetHeight_var = tk.StringVar(value=str(move.targetHeight))
        velocity_var = tk.StringVar(value=str(move.velocity))
        frontDelay_var = tk.StringVar(value=str(move.frontDelay))
        backDelay_var = tk.StringVar(value=str(move.backDelay))

        ttk.Label(frame, text='target height').grid(row=0, column=0)
        ttk.Label(frame, text='velocity').grid(row=0, column=1)
        ttk.Label(frame, text='front wait').grid(row=0, column=2)
        ttk.Label(frame, text='back wait').grid(row=0, column=3)
        ttk.Button(frame, text='execute', command=lambda: ((self.__executeMove(move), self.saveEntries(move, targetHeight_var, velocity_var, frontDelay_var, backDelay_var)))).grid(row=1, column=5, padx=15)
        ttk.Button(frame, text='save', command=lambda: (self.saveEntries(move, targetHeight_var, velocity_var, frontDelay_var, backDelay_var))).grid(row=1, column=4, padx=15)
        ttk.Button(frame, text='x', width=.3, command=lambda: self.__deleteMove(move,frame)).grid(row=0, column=5, sticky='ne', padx=20, pady=20)
        ttk.Entry(frame, textvariable=targetHeight_var).grid(row=1, column=0, sticky='new')  # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=velocity_var).grid(row=1, column=1, sticky='new')      # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=frontDelay_var).grid(row=1, column=2, sticky='new')    # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=backDelay_var).grid(row=1, column=3, sticky='new')     # Ensure entries expand horizontally

        return frame
    """save entries saves all the text variable entries to the move associated with the gui element."""
    def saveEntries(self, move, targetHeight_var, velocity_var, frontDelay_var, backDelay_var):
        try:
            move.targetHeight = str(targetHeight_var.get())
            move.velocity = str(velocity_var.get())
            move.frontDelay = int(frontDelay_var.get())
            move.backDelay = int(backDelay_var.get())
            print("MOVE:")
            print(f"targetHeight: {move.targetHeight}, velocity: {move.velocity}, frontDelay: {move.frontDelay}, backDelay: {move.backDelay}")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")


    """executemove makes a list only containing that move because startexecute thread needs to take a list
    so we are just wanting to execute this one move..."""
    def __executeMove(self, move):
        tempList = []
        tempList.append(move)
        self.gui.startExecuteThread(tempList, True)

    """deleteMove deletes the move that the user clicks the x on"""
    def __deleteMove(self, move, frame):
         # Check if the move is in the list
        if move in self.moveList:
            # Remove the move from the list
            self.moveList.remove(move)
            print(f"Removed move: {move}")  # Debug print
            # Destroy the frame containing the move
            frame.destroy()
            print(f"Destroyed frame: {frame}")  # Debug print
            # Update the canvas scrollregion
            self.updateList(self.moveList)
            self.update_size(None)
        else:
            print("Move not found in the list.")
