import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import Tk, Label, Button, filedialog, Frame
#TODO TAke out unnecessary imports 


def analyze_data_test(file_path):
     # Read CSV file
    df = pd.read_csv(file_path, usecols=[' Elapsed Time [hh:mm:ss:ms]', ' S 1 [mW]', ' S 2 [mW]', ' S 3 [mW]'])
    pd.set_option('display.precision', 6)
    # print(df)

    #this is all depending on the file, TODO: make standardized for many different files
    #put the data into appropriate vectors
    unformattedTimes = np.array(df[' Elapsed Time [hh:mm:ss:ms]'].values)
    timeList = [convert_to_new_format(value) for value in unformattedTimes]
    timeList = [float(x) for x in timeList]
    timeList = [.1*x for x in timeList]
    print(timeList)
   # print(timeList)
   # timeList = timeList * .2
    #print(timeList)
   # print("hello")
    s1List = np.array(df[' S 1 [mW]'].values)
    s2List = np.array(df[' S 2 [mW]'].values)
    s3List = np.array(df[' S 3 [mW]'].values)

def analyze_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path, usecols=[' Elapsed Time [hh:mm:ss:ms]', ' S 1 [mW]', ' S 2 [mW]', ' S 3 [mW]'])
    pd.set_option('display.precision', 6)
    # print(df)

    #this is all depending on the file, TODO: make standardized for many different files
    #put the data into appropriate vectors
    unformattedTimes = np.array(df[' Elapsed Time [hh:mm:ss:ms]'].values)
    timeList = [convert_to_new_format(value) for value in unformattedTimes]
    timeList = [float(x) for x in timeList]
    s1List = np.array(df[' S 1 [mW]'].values)
    s2List = np.array(df[' S 2 [mW]'].values)
    s3List = np.array(df[' S 3 [mW]'].values)


    #convert stokes vector to polar coordinates (radius = 1)
    #LAB: TALK TO DR. HARRISON ABOUT PRECISION
    sx = np.sqrt((s1List*s1List)+(s2List*s2List)) #tested
   # print("sx: " + str(sx))
    theta = np.arctan2(s2List,s1List) #tested
    #print("theta: " + str(theta))
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
   # print("theta after for loop: " + str(theta))
    #print(wrapCount)
   # print("wrapCount after for loop: " + str(wrapCount))


    n = len(theta) #tested
    #print("n: " + str(n))
   #print("n: " + str(n))
    xx=theta*theta #tested
   # print("xx: " + str(xx))
    yy=psi*psi #tested
   # print("yy: " + str(yy))
    xy=theta*psi #tested
   # print("xy " + str(xy))
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
    #print("a: " + str(a))


    xc = -0.5 * a[0] #tested
    #print("xc " + str(xc))
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
    thick = 3  # thickness of the samples in mm
    rate = 0.1  # rate of the micrometer (compression rate in mm/s)
    #print(timeList)
    ttimeList = [rate*x for x in timeList]
    strain = [x/thick for x in timeList]

    return timeList, strain, phase, s1List, s2List, s3List

# Function to convert the values
def convert_to_new_format(value):
    # Splitting the value by ':'
    components = value.split(':')
   # print(len(components))
   # print(components)
    # Check if the number of components is as expected
    if len(components) != 4:
        print("returning none")
        return None  # Return None for invalid values
    
    # Extracting hours, minutes, seconds, and milliseconds
 
    hours = float(components[0])  # Convert to float instead of int
    minutes = float(components[1])
    seconds = float(components[2])
    milliseconds = float(components[3])

    
    # Calculate the total milliseconds
    total_milliseconds = int((hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds)
    
    # Calculate the remaining milliseconds after the whole seconds
    remaining_milliseconds = total_milliseconds % 1000
    
    # Calculate the whole seconds
    whole_seconds = total_milliseconds // 1000
    
    # Format the result
    formatted_result = f"{whole_seconds}.{remaining_milliseconds}"
    return formatted_result

