import dataAnalysisVmaster
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import controller
#TODO: take out unnecessary imports
def run(ser):
    window = setupWindow(ser)
    window.mainloop()
    
   
def setupWindow(ser):
    window = tk.Tk()
    window.config(background="red")
    window.title("Data GUI")
    window.geometry("800x500")
    topMenu(window, ser)
    
    return window


def topMenu(window, ser):
    frameTopMenu = tk.Frame(window, width=1000, height=30)
    frameTopMenu.config(bg="blue")
    frameTopMenu.pack(side='top')
    frameTopMenu.pack_propagate(False)

    #buttons
    quitButton(frameTopMenu, window)
    micrometerControlButton(frameTopMenu, window, ser)
    browseDataFileButton(frameTopMenu, window)
    micrometerEnterDisableStateButton(frameTopMenu, window, ser)
    openMicrometerMenuButton(frameTopMenu, window, ser)
    

#button definitions - main window
def quitButton(frameTopMenu, window):
    quitButton = tk.Button(frameTopMenu, text="Quit", command=lambda: [window.quit()]) 
    quitButton.pack(side='right') 

def micrometerControlButton(frameTopMenu, window, ser):
    micrometerControlButton = tk.Button(frameTopMenu, text="initialize micrometer", command=lambda: [controller.goHome(ser)])
    micrometerControlButton.pack(side="left")

def micrometerEnterDisableStateButton(frameTopMenu, window, ser):
    micrometerEnterDisableStateButton = tk.Button(frameTopMenu, text="micrometer enter disable state", command=lambda: [controller.disable(ser)])
    micrometerEnterDisableStateButton.pack(side="left")

def browseDataFileButton(frameTopMenu, window):
    browseDataFileButton = tk.Button(frameTopMenu, text="browse for data file", command=lambda: [browse_file(window)])
    browseDataFileButton.pack(side='left')
    
def openMicrometerMenuButton(frameTopMenu, window, ser):
    openMicrometerMenu = tk.Button(frameTopMenu, text="micrometer menu", command=lambda: [micromenterControlWindow(ser)])
    openMicrometerMenu.pack(side="left")



# browse file button helper method
def browse_file(window):
    file_path = tk.filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    if(file_path):
        plot(file_path, window)


# analyzes data using dataAnalysisVmaster and plots data
def plot(file_path, window):
    timeList, strain, phase, s1List, s2List, s3List = dataAnalysisVmaster.analyze_data(file_path)
    
    # Write the analyzed data into a .csv file
    data = np.vstack((timeList, strain, phase)).T
    filename = 'analyzed_data.csv'
    np.savetxt(filename, data, delimiter=',', header='time (s),strain (mm/mm),phase (pi radians)', comments='')

    #setup tkinter frame for graphs
    frameGraphs = tk.Frame(window, width=800, height=400)
    frameGraphs.pack()
    frameGraphs.pack_propagate(False)

    # Plot phase vs. strain
    fig2, ax2 = plt.subplots()
    fig2.set_figheight(4)
    fig2.set_figwidth(4)
    ax2.plot(strain, phase)
    ax2.set_title('Phase vs. Strain')
    ax2.set_xlabel('Strain (mm/mm)')
    ax2.set_ylabel('Phase (pi radians)')
    
   
    # Embed the Matplotlib graph in Tkinter
    canvas1 = FigureCanvasTkAgg(fig2, master=frameGraphs)
    canvas1.get_tk_widget().pack(side="left")

    # Plot circle trace on sphere (for reference)
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(111, projection='3d')
    fig3.set_figheight(4)
    fig3.set_figwidth(5)
    phi = np.linspace(0, np.pi, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    phi, theta = np.meshgrid(phi, theta)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    ax3.plot_wireframe(x, y, z, color='r', alpha=0.5, linewidth=0.1)
    ax3.scatter(s1List, s2List, s3List)
    ax3.set_xlabel('s1')
    ax3.set_ylabel('s2')
    ax3.set_zlabel('s3')
    ax3.set_title('Circle Trace on Sphere')


    # Embed the Matplotlib graph in Tkinter
    canvas1 = FigureCanvasTkAgg(fig3, master=frameGraphs)
    canvas1_widget = canvas1.get_tk_widget()
    canvas1.get_tk_widget().pack(side="left")



def micromenterControlWindow(ser):
    
    # Toplevel object which will 
    # be treated as a new window
    micrometerWindow = tk.Tk()

    # sets the title of the
    # Toplevel widget
    micrometerWindow.title("New Window")

    # sets the geometry of toplevel
    micrometerWindow.geometry("400x400")

    # A Label widget to show in toplevel
    tk.Label(micrometerWindow, 
            text ="micrometer controls").pack()
    
    micrometerButtons(micrometerWindow, ser)


#micrometer control window buttons:
def micrometerButtons(micrometerWindow, ser) : 
    micrometerMenu = tk.Frame(micrometerWindow, width=1000, height=500)
    micrometerMenu.config(bg="blue")
    micrometerMenu.pack(side='top')
    micrometerMenu.pack_propagate(False)
    setHeightFrame(micrometerMenu, micrometerWindow, ser)



def setHeightFrame(frame, micrometerWindow, ser):
    heightFrame = tk.Frame(frame, width=100, height=100)
    heightFrame.config(bg="green")
    heightFrame.pack(side="left")
    heightFrame.pack_propagate(False)

    setHeightLabel = tk.Label(heightFrame, text="Set the height")
    inputtxt = tk.Text(heightFrame, height = 1, width = 10) 
     
    setHeightButton = tk.Button(heightFrame, text="goTo", command=lambda: [controller.goToHeight(inputtxt.get("1.0", "end-1c") , ser)])
    setHeightButton.pack(side="bottom")
    inputtxt.pack(side="bottom")
    setHeightLabel.pack(side="top")
   
                   









