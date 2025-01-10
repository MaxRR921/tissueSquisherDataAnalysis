# tissueSquisherDataAnalysis
Data analysis code for tissue squisher

must have numpy, pandas, matplotLib, tkinter, pyserial, ctypes all installed

To run, in directory type python main.py

python 3.11.7


# DEVS:

Always use camelCase. use UpperCamelCase for class names, and never declare member variables outside of __init__ or other methods. 


The general structure is as follows:



## For creating new UI follow this format:


### New Window Description
    new file: xxGui
    in this file:
    class XxGui:
        def __init__(self):
            self.window = tk.Tk()
            self.window.config(background="xx")
            self.window.title("title")
            self.window.geometry("nnnxnnn")
            //instantiate any other nested windows that can be opened with buttons here, for example:
            self.contGui = controllerGui.ControllerGui()

        run should be the only public method in a Gui class
        def run(self):
            //any other elements and/or buttons in the ui, for example:
            __topMenu()
            self.window.mainloop()

        def __topMenu(self):
            **creating frame for the top menu at the top of the window**
            frameTopMenu = tk.Frame(self.window, width=1000, height=30)
            frameTopMenu.config(bg="blue")
            frameTopMenu.pack(side='top')
            frameTopMenu.pack_propagate(False)

            **functions for all the buttons in the top menu should always have __quitButton**
            self.__quitButton(frameTopMenu)
            **this button will open a nested window, the object for which was instantiated in __init__**
            self.__openMicrometerMenuButton(frameTopMenu)

        def __quitButton(self, frameTopMenu):
            quitButton = tk.Button(frameTopMenu, text="Quit", command=lambda: [self.window.quit()]) 
            quitButton.pack(side='right') 


        def __openMicrometerMenuButton(self, frameTopMenu):
            **creating a button to run the controllerGui window**
            openMicrometerMenu = tk.Button(frameTopMenu, text="micrometer menu", command=lambda: [self.contGui.run()])
            openMicrometerMenu.pack(side="left")



# TEMPLATE    

class ItemGui:
    def __init__(self):
        self.window = tk.Tk()
        self.window.config(background="red")
        self.window.title("Data GUI")
        self.window.geometry("800x500")
        self.contGui = controllerGui.ControllerGui()
        self.polGui = polarimeterGui.PolarimeterGui()

    def run(self):
        self.__topMenu()
        self.window.mainloop()
    
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
