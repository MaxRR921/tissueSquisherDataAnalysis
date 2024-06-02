import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import Tk, Label, Button, filedialog, Frame
#TODO TAke out unnecessary imports 

class data_analyzer:

    s1List = np.array([])
    s2List = np.array([])
    s3List = np.array([])
    timeList = np.array([])

    @classmethod
    def analyze_data(cls, s1, s2, s3, time):
        #this is bad. will later need to use a different data structure
        s1_temp = np.array([s1])
        s2_temp = np.array([s2])
        s3_temp = np.array([s3])
        time_temp = np.array([time])
        cls.s1List = np.concatenate((cls.s1List, s1_temp))
        cls.s2List = np.concatenate((cls.s2List, s2_temp))
        cls.s3List = np.concatenate((cls.s3List, s3_temp))
        cls.timeList = np.concatenate((cls.timeList, time_temp))

         #convert stokes vector to polar coordinates (radius = 1)
        #LAB: TALK TO DR. HARRISON ABOUT PRECISION
        sx = np.sqrt((cls.s1List*cls.s1List)+(cls.s2List*cls.s2List)) #tested
        #print("sx: " + str(sx))
        theta = np.arctan2(cls.s2List,cls.s1List) #tested
    # print("theta: " + str(theta))
        psi = np.arctan2(cls.s3List, sx) #tested
        #print("psi: " + str(psi))


        wrapCount = 0 #tested
        #print("wrapcount: " + str(wrapCount))
        thetaCounter = np.zeros(len(theta)) #tested
    # print("thetaCounter: " + str(thetaCounter))

        # theta can have sign issues based on where it is on the sphere.
        # This code fixes those problems by making sure there isn't a sudden sign-change jump. ???
        for i in range(len(theta) - 1):
            if np.sign(cls.s1List[i]) == -1:
                if (np.sign(cls.s2List[i]) == 1) and (np.sign(cls.s2List[i + 1]) == -1):
                    wrapCount += 2 * np.pi
                elif (np.sign(cls.s2List[i]) == -1) and (np.sign(cls.s2List[i + 1]) == 1):
                    wrapCount -= 2 * np.pi
            thetaCounter[i+1]= wrapCount;


        theta = theta + thetaCounter; #tested
        #print("theta after for loop: " + str(theta))
        #print(wrapCount)
    # print("wrapCount after for loop: " + str(wrapCount))


        n = len(theta) #tested
        #print("n: " + str(n))
        #print("n: " + str(n))
        xx=theta*theta #tested
        #print("xx: " + str(xx))
        yy=psi*psi #tested
    # print("yy: " + str(yy))
        xy=theta*psi #tested
    #print("xy " + str(xy))
        #A=[sum(theta) sum(psi) n;sum(xy) sum(yy) sum(psi);sum(xx) sum(xy) sum(theta)]
        A = np.array([[np.sum(theta), np.sum(psi), n],
                    [np.sum(xy), np.sum(yy), np.sum(psi)],
                    [np.sum(xx), np.sum(xy), np.sum(theta)]]) #tested
        print("A " + str(A))
        det = np.linalg.det(A)
        print("determinant is:")
        print(det)
        print("that was det")
        
        B = np.array([
            -np.sum(xx + yy),
            -np.sum(xx * psi + yy * psi),
            -np.sum(xx * theta + xy * psi)
        ]) #tested
        #print("B: " + str(B))

        if(np.linalg(det(A)) != 0):
            a = np.linalg.solve(A, B) #solves for x vector in Ax = B #tested

        # print("a: " + str(a))


            xc = -0.5 * a[0] #tested
        # print("xc " + str(xc))
            yc = -0.5 * a[1] #tested
        # print("yc " + str(yc))
            R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2]) #tested
        # print("R " + str(R))


            # Create x and y coordinates with rotation
            x = cls.s1List * np.sin(-xc) + cls.s2List * np.cos(-xc)
            y = cls.s3List

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
            strain = (cls.timeList * rate) / thick
            print(cls.timeList)
            print(strain)
            print(phase)
            print(cls.s1List)
            print(cls.s2List)
            return cls.timeList, strain, phase, cls.s1List, cls.s2List, cls.s3List
        else:
            return "error"




    
   
    
    

def analyze_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path, usecols=['Time Stamp [s]', 'Stokes 1', 'Stokes 2', 'Stokes 3'])
    pd.set_option('display.precision', 6)
    #print(df)
    
    #this is all depending on the file, TODO: make standardized for many different files
    #put the data into appropriate vectors
    timeList = np.array(df['Time Stamp [s]'].values)
   #print("timeList Length: " + str(len(timeList)))
    s1List = np.array(df['Stokes 1'].values)
    s2List = np.array(df['Stokes 2'].values)
    s3List = np.array(df['Stokes 3'].values)


    #convert stokes vector to polar coordinates (radius = 1)
    #LAB: TALK TO DR. HARRISON ABOUT PRECISION
    sx = np.sqrt((s1List*s1List)+(s2List*s2List)) #tested
    #print("sx: " + str(sx))
    theta = np.arctan2(s2List,s1List) #tested
   # print("theta: " + str(theta))
    psi = np.arctan2(s3List, sx) #tested
    #print("psi: " + str(psi))


    wrapCount = 0 #tested
    #print("wrapcount: " + str(wrapCount))
    thetaCounter = np.zeros(len(theta)) #tested
   # print("thetaCounter: " + str(thetaCounter))

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
    #print("theta after for loop: " + str(theta))
    #print(wrapCount)
   # print("wrapCount after for loop: " + str(wrapCount))


    n = len(theta) #tested
    #print("n: " + str(n))
    #print("n: " + str(n))
    xx=theta*theta #tested
    #print("xx: " + str(xx))
    yy=psi*psi #tested
   # print("yy: " + str(yy))
    xy=theta*psi #tested
   #print("xy " + str(xy))
    #A=[sum(theta) sum(psi) n;sum(xy) sum(yy) sum(psi);sum(xx) sum(xy) sum(theta)]
    A = np.array([[np.sum(theta), np.sum(psi), n],
                [np.sum(xy), np.sum(yy), np.sum(psi)],
                [np.sum(xx), np.sum(xy), np.sum(theta)]]) #tested
   # print("A " + str(A))

    B = np.array([
        -np.sum(xx + yy),
        -np.sum(xx * psi + yy * psi),
        -np.sum(xx * theta + xy * psi)
    ]) #tested
    #print("B: " + str(B))


    a = np.linalg.solve(A, B) #solves for x vector in Ax = B #tested
   # print("a: " + str(a))


    xc = -0.5 * a[0] #tested
   # print("xc " + str(xc))
    yc = -0.5 * a[1] #tested
   # print("yc " + str(yc))
    R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2]) #tested
   # print("R " + str(R))


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
    print(timeList)
    print(strain)
    print(phase)
    print(s1List)
    print(s2List)
    return timeList, strain, phase, s1List, s2List, s3List



