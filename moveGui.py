import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from threading import Thread

class MoveGui(ttk.Frame):
    def __init__(self, parent, moveList, item_height, width):
        super().__init__(master=parent)
        self.pack(expand=True, fill='both', anchor="nw")
        
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

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")

    def updateList(self, moveList):
        self.moveList = moveList
        self.item_number = len(moveList)
        self.canvas.configure(scrollregion=(0, 0, self.width, self.item_number * self.item_height))

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.populate_items()
        self.update_size(None)

    def populate_items(self):
        for index, move in enumerate(self.moveList):
            self.create_item(move).pack(expand=True, fill='both', pady=4, padx=10)

    def update_size(self, event):
        canvas_width = self.winfo_width()
        canvas_height = self.item_number * self.item_height
        self.canvas.itemconfig(self.frame_id, width=canvas_width, height=canvas_height)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

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
        ttk.Button(frame, text='save', command=lambda: self.saveEntries(move, targetHeight_var, velocity_var, frontDelay_var, backDelay_var)).grid(row=1, column=4,)
        ttk.Entry(frame, textvariable=targetHeight_var).grid(row=1, column=0, sticky='new')  # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=velocity_var).grid(row=1, column=1, sticky='new')      # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=frontDelay_var).grid(row=1, column=2, sticky='new')    # Ensure entries expand horizontally
        ttk.Entry(frame, textvariable=backDelay_var).grid(row=1, column=3, sticky='new')     # Ensure entries expand horizontally

        return frame

        return frame

    def saveEntries(self, move, targetHeight_var, velocity_var, frontDelay_var, backDelay_var):
        try:
            move.targetHeight = str(targetHeight_var.get())
            move.velocity = str(velocity_var.get())
            move.frontDelay = str(frontDelay_var.get())
            move.backDelay = str(backDelay_var.get())
            print("MOVE:")
            print(f"targetHeight: {move.targetHeight}, velocity: {move.velocity}, frontDelay: {move.frontDelay}, backDelay: {move.backDelay}")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")