import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import Tk, Label, Button, filedialog, Frame
#TODO TAke out unnecessary imports 

def convert_time_format(time_list):
    def convert_single_time(time_str):
        # Strip any leading/trailing whitespace
        time_str = time_str.strip()
        
        # Split the string by ':' to get hours, minutes, seconds, and milliseconds
        parts = time_str.split(':')
        
        if len(parts) == 4:
            try:
                # Extract hours, minutes, seconds, and milliseconds
                hours = float(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                milliseconds = int(parts[3])
                
                # Convert everything to seconds and combine
                total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
                return total_seconds
            except ValueError:
                # Return NaN if there's a conversion error
                return float('nan')
        else:
            # Return NaN if the format is incorrect
            return float('nan')
    
    # Apply the conversion to each element in the list
    return np.array([convert_single_time(time_str) for time_str in time_list])

def analyze_data(file_path):
    # Read CSV file
    df = pd.read_csv(file_path, usecols=[' Elapsed Time [hh:mm:ss:ms]', ' Normalized s 1 ', ' Normalized s 2 ', ' Normalized s 3 '])
    pd.set_option('display.precision', 6)
    #print(df)
    
    #this is all depending on the file, TODO: make standardized for many different files
    #put the data into appropriate vectors
    timeList = np.array(df[' Elapsed Time [hh:mm:ss:ms]'].values)
    timeList = convert_time_format(timeList)
    print(timeList)
    
    print("timeList Length: " + str(len(timeList)))
    
    # Clean the 'Normalized s 1', 'Normalized s 2', and 'Normalized s 3' columns
    s1List = pd.to_numeric(df[' Normalized s 1 '], errors='coerce').values
    s2List = pd.to_numeric(df[' Normalized s 2 '], errors='coerce').values
    s3List = pd.to_numeric(df[' Normalized s 3 '], errors='coerce').values
    
    # Convert to numpy arrays
    s1List = np.array(s1List)
    s2List = np.array(s2List)
    s3List = np.array(s3List)
    
    print("Is there any NaN in s1?", np.isnan(s1List).any())
    print("Is there any NaN in s2?", np.isnan(s2List).any())
    print("Is there any NaN in s3?", np.isnan(s3List).any())
    s1List = pd.Series(s1List).fillna(method='ffill').values
    s2List = pd.Series(s2List).fillna(method='ffill').values
    s3List = pd.Series(s3List).fillna(method='ffill').values



#     #convert stokes vector to polar coordinates (radius = 1)
#     #LAB: TALK TO DR. HARRISON ABOUT PRECISION
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
    print(wrapCount)
    print("wrapCount after for loop: " + str(wrapCount))

    print("Is there any NaN in theta?", np.isnan(theta).any())
    print("Is there any NaN in psi?", np.isnan(psi).any())
    print("Is there any inf in theta?", np.isinf(theta).any())
    print("Is there any inf in psi?", np.isinf(psi).any())

    n = len(theta) #tested
    print("n: " + str(n))
    print("n: " + str(n))
    xx=theta*theta #tested
    print("xx: " + str(xx))
    yy=psi*psi #tested
    print("yy: " + str(yy))
    xy=theta*psi #tested
    print("xy " + str(xy))
    # A=[sum(theta) sum(psi) n;sum(xy) sum(yy) sum(psi);sum(xx) sum(xy) sum(theta)]
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
    print("X:")
    print(x)
    y = s3List
    print("Y:")
    print(y)

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
    print("STRAIN:")
    print(strain)
    print("PHASE")
    print(phase)
    print("DONE")
    #print(s1List)
    #print(s2List)
    return timeList, strain, phase, s1List, s2List, s3List

