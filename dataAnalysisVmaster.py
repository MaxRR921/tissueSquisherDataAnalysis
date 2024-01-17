import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Label, Button, filedialog, Frame






def analyze_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path, usecols=['Time Stamp [s]', 'Stokes 1', 'Stokes 2', 'Stokes 3'])

    pd.set_option('display.precision', 6)
    print(df)

    #this is all depending on the file, TODO: make standardized for many different files
    #put the data into appropriate vectors
    timeList = np.array(df['Time Stamp [s]'].values)
    print("timeList Length: " + str(len(timeList)))
    s1List = np.array(df['Stokes 1'].values)
    s2List = np.array(df['Stokes 2'].values)
    s3List = np.array(df['Stokes 3'].values)




    #convert stokes vector to polar coordinates (radius = 1)
    #LAB: TALK TO DR. HARRISON ABOUT PRECISION
    sx = np.sqrt((s1List*s1List)+(s2List*s2List)) #tested
    print("sx: " + str(sx))
    theta = np.arctan2(s2List,s1List) #tested
    print("theta: " + str(theta))
    psi = np.arctan2(s3List, sx) #tested
    print("psi: " + str(psi))


    wrapCount = 0 #tested
    print("wrapcount: " + str(wrapCount))
    thetaCounter = np.zeros(len(theta)) #tested
    print("thetaCounter: " + str(thetaCounter))

    # theta can have sign issues based on where it is on the sphere.
    # This code fixes those problems by making sure there isn't a sudden sign-change jump. ???
    for i in range(len(theta) - 1):
        if np.sign(s1List[i]) == -1:
            if (np.sign(s2List[i]) == 1) and (np.sign(s2List[i + 1]) == -1):
                wrapCount += 2 * np.pi
            elif (np.sign(s2List[i]) == -1) and (np.sign(s2List[i + 1]) == 1):
                wrapCount -= 2 * np.pi
        thetaCounter[i+1]= wrapCount;


    theta = theta + thetaCounter; #tested
    print("theta after for loop: " + str(theta))
    #print(wrapCount)
    print("wrapCount after for loop: " + str(wrapCount))


    n = len(theta) #tested
    print("n: " + str(n))
    print("n: " + str(n))
    xx=theta*theta #tested
    print("xx: " + str(xx))
    yy=psi*psi #tested
    print("yy: " + str(yy))
    xy=theta*psi #tested
    print("xy " + str(xy))
    #A=[sum(theta) sum(psi) n;sum(xy) sum(yy) sum(psi);sum(xx) sum(xy) sum(theta)]
    A = np.array([[np.sum(theta), np.sum(psi), n],
                [np.sum(xy), np.sum(yy), np.sum(psi)],
                [np.sum(xx), np.sum(xy), np.sum(theta)]]) #tested
    print("A " + str(A))

    B = np.array([
        -np.sum(xx + yy),
        -np.sum(xx * psi + yy * psi),
        -np.sum(xx * theta + xy * psi)
    ]) #tested
    print("B: " + str(B))


    a = np.linalg.solve(A, B) #solves for x vector in Ax = B #tested
    print("a: " + str(a))


    xc = -0.5 * a[0] #tested
    print("xc " + str(xc))
    yc = -0.5 * a[1] #tested
    print("yc " + str(yc))
    R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2]) #tested
    print("R " + str(R))


    # Create x and y coordinates with rotation
    x = s1List * np.sin(-xc) + s2List * np.cos(-xc)
    y = s3List

    # Find the angle of the circle (phase)
    phase = np.arctan2(y, x) / np.pi

    # Normalize the phase
    k = len(phase)
    phaseCounter = np.zeros(k)
    wrapCount = 0

    # Check for sign changes and update phaseCounter
    for i in range(k-1):
        if np.sign(x[i]) == -1:
            if (np.sign(y[i]) == 1) and (np.sign(y[i+1]) == -1):
                wrapCount += 2
            elif (np.sign(y[i]) == -1) and (np.sign(y[i+1]) == 1):
                wrapCount -= 2
        phaseCounter[i+1] = wrapCount

    phase = (phase + phaseCounter - phase[0])  # Normalize phase

    # Convert time to strain based on rate of micrometer motion
    thick = 5.28  # thickness of the samples in mm
    rate = 0.1  # rate of the micrometer (compression rate in mm/s)
    strain = (timeList * rate) / thick

    return timeList, strain, phase, s1List, s2List, s3List

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
    if file_path:
        timeList, strain, phase, s1List, s2List, s3List = analyze_data(file_path)
        window = Tk()
        window.title("Data Analysis Results")

        frame = Frame(window)
        frame.pack()




       # Plot phase vs. time
        fig1, ax1 = plt.subplots()
        ax1.plot(timeList, phase)
        ax1.set_title('Phase vs. Time')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Phase (*/pi radians)')

        canvas1 = FigureCanvasTkAgg(fig1, master=frame)
        canvas1.get_tk_widget().pack()

        # Write the analyzed data into a .csv file
        data = np.vstack((timeList, strain, phase)).T
        filename = 'analyzed_data.csv'
        np.savetxt(filename, data, delimiter=',', header='time (s),strain (mm/mm),phase (pi radians)', comments='')

        # Plot phase vs. strain
        fig2, ax2 = plt.subplots()
        ax2.plot(strain, phase)
        ax2.set_title('Phase vs. Strain')
        ax2.set_xlabel('Strain (mm/mm)')
        ax2.set_ylabel('Phase (pi radians)')

        # Plot circle trace on sphere (for reference)
        fig3 = plt.figure()
        ax3 = fig3.add_subplot(111, projection='3d')

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

        plt.show()


# Create Tkinter window
root = Tk()
root.title("Data Analysis GUI")

# Add label and button to the window
label = Label(root, text="Click the button to select a CSV file:")
label.pack(pady=10)

button = Button(root, text="Browse", command=browse_file)
button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()