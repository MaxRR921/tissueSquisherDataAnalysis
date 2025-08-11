import numpy as np
import pandas as pd
import multiprocessing 
import threading
import polarimeterCalibration
import matplotlib.pyplot as plt
#TODO TAke out unnecessary imports 


class DataAnalyzer:
    
    def __init__(self):
        self.strainQueue = multiprocessing.Queue()
        self.phaseQueue = multiprocessing.Queue()
        self.strain = None 
        self.phase = None
        self.finishAnalyzeDataSignal = threading.Event()
    


    def analyzeData(self, s1Queue, s2Queue, s3Queue, timeQueue):
        self.strain = None 
        self.phase = None
        # Convert lists to numpy arrays
        s1List = []
        s2List = []
        s3List = []


        timeList = []
        while not s1Queue.empty():
            s1List.append(s1Queue.get()) 

        while not s2Queue.empty():
            s2List.append(s2Queue.get()) 

        while not s3Queue.empty():
            s3List.append(s3Queue.get()) 

        while not timeQueue.empty():
            timeList.append(timeQueue.get())

        s1ListNp = np.array(s1List)
        s2ListNp = np.array(s2List)
        s3ListNp = np.array(s3List)
        timeListNp = np.array(timeList)
        self.polCalibrator = polarimeterCalibration.PolarimeterCalibrator(s1List, s2List, s3List)

        


        # Check if input lists are empty
        if len(s1ListNp) == 0 or len(s2ListNp) == 0 or len(s3ListNp) == 0 or len(timeListNp) == 0:
            print("Error: One or more input lists are empty.")
            return None, None

        # Convert Stokes vector to polar coordinates
        sx = np.sqrt((s1ListNp * s1ListNp) + (s2ListNp * s2ListNp))
        theta = np.arctan2(s2ListNp, s1ListNp)
        psi = np.arctan2(s3ListNp, sx)

        wrapCount = 0
        thetaCounter = np.zeros(len(theta))

        # Fix sign issues in theta
        for i in range(len(theta) - 1):
            if np.sign(s1ListNp[i]) == -1:
                if (np.sign(s2ListNp[i]) == 1) and (np.sign(s2ListNp[i + 1]) == -1):
                    wrapCount += 2 * np.pi
                elif (np.sign(s2ListNp[i]) == -1) and (np.sign(s2ListNp[i + 1]) == 1):
                    wrapCount -= 2 * np.pi
            thetaCounter[i+1] = wrapCount

        theta = theta + thetaCounter

        n = len(theta)
        xx = theta * theta
        yy = psi * psi
        xy = theta * psi

        A = np.array([[np.sum(theta), np.sum(psi), n],
                    [np.sum(xy), np.sum(yy), np.sum(psi)],
                    [np.sum(xx), np.sum(xy), np.sum(theta)]])
        
        B = np.array([
            -np.sum(xx + yy),
            -np.sum(xx * psi + yy * psi),
            -np.sum(xx * theta + xy * psi)
        ])

        # Print A and B to debug
        print("Matrix A:", A)
        print("Matrix B:", B)

        # Add regularization to A to avoid singular matrix error
        epsilon = 1e-10
        A += epsilon * np.eye(A.shape[0])

        try:
            a = np.linalg.solve(A, B)
        except np.linalg.LinAlgError as e:
            print(f"Error solving linear system: {e}")
            return None, None

        xc = -0.5 * a[0]
        yc = -0.5 * a[1]
        R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2])

        # Create x and y coordinates with rotation
        x = s1ListNp * np.sin(-xc) + s2ListNp * np.cos(-xc)
        y = s3ListNp

        # Find the angle of the circle (phase)
        self.phase = np.arctan2(y, x) / np.pi

        # Normalize the phase
        k = len(self.phase)
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

        if len(self.phase) == 0:
            print("Error: phase array is empty.")
            return None, None

        self.phase = (self.phase + phaseCounter - self.phase[0])  # Normalize phase

        # Convert time to strain based on rate of micrometer motion
        thick = 5.28  # thickness of the samples in mm
        rate = 0.1  # rate of the micrometer (compression rate in mm/s)
        self.strain = (timeListNp * rate) / thick
        
        # print("Time List:", timeListNp)
        # print("Strain:", self.strain)
        try:
            print("Phase: ", self.phase)
            print("Strain: ", self.strain)
            # print("S1 List:", s1ListNp)
            # print("S2 List:", s2ListNp)
            # print("S3 List: ", s3ListNp)
        except:
            print("UH OH")
        for s in self.strain:
            self.strainQueue.put(s)
        for p in self.phase:
            self.phaseQueue.put(p)
        self.finishAnalyzeDataSignal.set()





    def analyzeDataNoRealtime(self, s1, s2, s3, time):
        self.strain = None 
        self.phase = None
        # Convert lists to numpy arrays
        s1List = s1
        s2List = s2
        s3List = s3


        timeList = time

        s1ListNp = np.array(s1List)
        s2ListNp = np.array(s2List)
        s3ListNp = np.array(s3List)
        timeListNp = np.array(timeList)

        


        # Check if input lists are empty
        if len(s1ListNp) == 0 or len(s2ListNp) == 0 or len(s3ListNp) == 0 or len(timeListNp) == 0:
            print("Error: One or more input lists are empty.")
            return None, None

        # Convert Stokes vector to polar coordinates
        sx = np.sqrt((s1ListNp * s1ListNp) + (s2ListNp * s2ListNp))
        theta = np.arctan2(s2ListNp, s1ListNp)
        psi = np.arctan2(s3ListNp, sx)

        wrapCount = 0
        thetaCounter = np.zeros(len(theta))

        # Fix sign issues in theta
        for i in range(len(theta) - 1):
            if np.sign(s1ListNp[i]) == -1:
                if (np.sign(s2ListNp[i]) == 1) and (np.sign(s2ListNp[i + 1]) == -1):
                    wrapCount += 2 * np.pi
                elif (np.sign(s2ListNp[i]) == -1) and (np.sign(s2ListNp[i + 1]) == 1):
                    wrapCount -= 2 * np.pi
            thetaCounter[i+1] = wrapCount

        theta = theta + thetaCounter

        n = len(theta)
        xx = theta * theta
        yy = psi * psi
        xy = theta * psi

        A = np.array([[np.sum(theta), np.sum(psi), n],
                    [np.sum(xy), np.sum(yy), np.sum(psi)],
                    [np.sum(xx), np.sum(xy), np.sum(theta)]])
        
        B = np.array([
            -np.sum(xx + yy),
            -np.sum(xx * psi + yy * psi),
            -np.sum(xx * theta + xy * psi)
        ])

        # Print A and B to debug
        print("Matrix A:", A)
        print("Matrix B:", B)

        # Add regularization to A to avoid singular matrix error
        epsilon = 1e-10
        A += epsilon * np.eye(A.shape[0])

        try:
            a = np.linalg.solve(A, B)
        except np.linalg.LinAlgError as e:
            print(f"Error solving linear system: {e}")
            return None, None

        xc = -0.5 * a[0]
        yc = -0.5 * a[1]
        R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2])

        # Create x and y coordinates with rotation
        x = s1ListNp * np.sin(-xc) + s2ListNp * np.cos(-xc)
        y = s3ListNp

        # Find the angle of the circle (phase)
        self.phase = np.arctan2(y, x) / np.pi

        # Normalize the phase
        k = len(self.phase)
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

        if len(self.phase) == 0:
            print("Error: phase array is empty.")
            return None, None

        self.phase = (self.phase + phaseCounter - self.phase[0])  # Normalize phase

        # Convert time to strain based on rate of micrometer motion
        thick = 5.28  # thickness of the samples in mm
        rate = 0.1  # rate of the micrometer (compression rate in mm/s)
        self.strain = (timeListNp * rate) / thick
        
        # print("Time List:", timeListNp)
        # print("Strain:", self.strain)
        try:
            print("Phase: ", self.phase)
            print("Strain: ", self.strain)
            # print("S1 List:", s1ListNp)
            # print("S2 List:", s2ListNp)
            # print("S3 List: ", s3ListNp)
        except:
            print("UH OH")
   
        plt.figure()
        plt.plot(self.strain, self.phase, marker='o')
        plt.xlabel("Strain")
        plt.ylabel("Phase")
        plt.title("Phase vs Strain")
        plt.grid(True)


    def s2_s3_from_s1_angles(self, s1, beta, gamma, prev_s3=None, eps=1e-9):
        """
        Compute normalized s2, s3 from normalized s1 and angles beta, gamma.
        Returns (s2, s3).
        """
        theta_c =  2.0 * gamma
        d = np.sin(2.0 * beta)  # equatorial offset
        r = np.cos(2.0 * beta)  # radius on sphere

        sin_tc = np.sin(theta_c)
        cos_tc = np.cos(theta_c)

        if abs(sin_tc) < eps or abs(r) < eps:
            raise ValueError("Degenerate geometry: need another observable or a prior sample.")

        # Solve cos(phi) from s1
        cos_phi = (d * cos_tc - s1) / (r * sin_tc)
        cos_phi = np.clip(cos_phi, -1.0, 1.0)

        # Compute normalized s2 and s3
        s2 = d * sin_tc + r * cos_phi * cos_tc
        s3_abs = abs(r) * np.sqrt(max(0.0, 1.0 - cos_phi**2))
        s3 = (np.sign(prev_s3) if (prev_s3 is not None and prev_s3 != 0) else 1.0) * s3_abs

        return s2, s3


    def write_stokes_csv(self, time_arr, s1_arr, beta, gamma, out_path="power_diff_for_matlab.csv"):
        """
        Vectorized helper: takes time[] and s1[] (normalized), computes s2[], s3[] using
        s2_s3_from_s1_angles with sign continuity, and writes a CSV with columns:
        Time,S1,S2,S3  (header included), suitable for the MATLAB script.

        Parameters
        ----------
        time_arr : array-like
            Timestamps (any numeric units).
        s1_arr : array-like
            Normalized S1/S0 values in [-1, 1].
        beta, gamma : float
            Same angle definitions used by your solver (radians).
        out_path : str
            Output CSV filename.
        """
        time_arr = np.asarray(time_arr, dtype=float).ravel()
        s1_arr   = np.asarray(s1_arr,   dtype=float).ravel()

        if time_arr.shape != s1_arr.shape:
            raise ValueError("time_arr and s1_arr must have the same shape")

        s2_list = np.empty_like(s1_arr, dtype=float)
        s3_list = np.empty_like(s1_arr, dtype=float)

        prev_s3 = None
        for i, s1 in enumerate(s1_arr):
            try:
                s2, s3 = self.s2_s3_from_s1_angles(s1, beta, gamma, prev_s3=prev_s3)
            except ValueError:
                # Degenerate geometry at this sample — write NaNs to keep indexing aligned
                s2, s3 = np.nan, np.nan
            s2_list[i] = s2
            s3_list[i] = s3
            # Preserve sign continuity for next step when we didn't hit a degenerate case
            if not (np.isnan(s3)):
                prev_s3 = s3

        # Compose table and write. We use numpy.savetxt to avoid extra deps.
        header = "Time,S1,S2,S3"
        data = np.column_stack([time_arr, s1_arr, s2_list, s3_list])
        np.savetxt(out_path, data, delimiter=",", header=header, comments="", fmt="%.10g")
        return out_path



# def analyze_data(self, file_path):
#     # Read CSV file
#     df = pd.read_csv(file_path, usecols=['Time Stamp [s]', 'Stokes 1', 'Stokes 2', 'Stokes 3'])
#     pd.set_option('display.precision', 6)
#     #print(df)
    
#     #this is all depending on the file, TODO: make standardized for many different files
#     #put the data into appropriate vectors
#     timeList = np.array(df['Time Stamp [s]'].values)
# #print("timeList Length: " + str(len(timeList)))
#     s1List = np.array(df['Stokes 1'].values)
#     s2List = np.array(df['Stokes 2'].values)
#     s3List = np.array(df['Stokes 3'].values)


#     #convert stokes vector to polar coordinates (radius = 1)
#     #LAB: TALK TO DR. HARRISON ABOUT PRECISION
#     sx = np.sqrt((s1List*s1List)+(s2List*s2List)) #tested
#     #print("sx: " + str(sx))
#     theta = np.arctan2(s2List,s1List) #tested
# # print("theta: " + str(theta))
#     psi = np.arctan2(s3List, sx) #tested
#     #print("psi: " + str(psi))


#     wrapCount = 0 #tested
#     #print("wrapcount: " + str(wrapCount))
#     thetaCounter = np.zeros(len(theta)) #tested
# # print("thetaCounter: " + str(thetaCounter))

#     # theta can have sign issues based on where it is on the sphere.
#     # This code fixes those problems by making sure there isn't a sudden sign-change jump. ???
#     for i in range(len(theta) - 1):
#         if np.sign(s1List[i]) == -1:
#             if (np.sign(s2List[i]) == 1) and (np.sign(s2List[i + 1]) == -1):
#                 wrapCount += 2 * np.pi
#             elif (np.sign(s2List[i]) == -1) and (np.sign(s2List[i + 1]) == 1):
#                 wrapCount -= 2 * np.pi
#         thetaCounter[i+1]= wrapCount;


#     theta = theta + thetaCounter; #tested
#     #print("theta after for loop: " + str(theta))
#     #print(wrapCount)
#     #print("wrapCount after for loop: " + str(wrapCount))


#     n = len(theta) #tested
#     #print("n: " + str(n))
#     #print("n: " + str(n))
#     xx=theta*theta #tested
#     #print("xx: " + str(xx))
#     yy=psi*psi #tested
#     #print("yy: " + str(yy))
#     xy=theta*psi #tested
# #print("xy " + str(xy))
#     #A=[sum(theta) sum(psi) n;sum(xy) sum(yy) sum(psi);sum(xx) sum(xy) sum(theta)]
#     A = np.array([[np.sum(theta), np.sum(psi), n],
#                 [np.sum(xy), np.sum(yy), np.sum(psi)],
#                 [np.sum(xx), np.sum(xy), np.sum(theta)]]) #tested
# # print("A " + str(A))

#     B = np.array([
#         -np.sum(xx + yy),
#         -np.sum(xx * psi + yy * psi),
#         -np.sum(xx * theta + xy * psi)
#     ]) #tested
#     #print("B: " + str(B))


#     a = np.linalg.solve(A, B) #solves for x vector in Ax = B #tested
# # print("a: " + str(a))


#     xc = -0.5 * a[0] #tested
# # print("xc " + str(xc))
#     yc = -0.5 * a[1] #tested
# # print("yc " + str(yc))
#     R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2]) #tested
# # print("R " + str(R))


#     # Create x and y coordinates with rotation
#     x = s1List * np.sin(-xc) + s2List * np.cos(-xc)
#     y = s3List

#     # Find the angle of the circle (phase)
#     self.phase = np.arctan2(y, x) / np.pi

#     # Normalize the phase
#     k = len(self.phase)
#     phaseCounter = np.zeros(k)
#     wrapCount = 0

#     # Check for sign changes and update phaseCounter
#     for i in range(k-1):
#         if np.sign(x[i]) == -1:
#             if (np.sign(y[i]) == 1) and (np.sign(y[i+1]) == -1):
#                 wrapCount += 2
#             elif (np.sign(y[i]) == -1) and (np.sign(y[i+1]) == 1):
#                 wrapCount -= 2
#         phaseCounter[i+1] = wrapCount

#     self.phase = (self.phase + phaseCounter - self.phase[0])  # Normalize phase (CHANGE IN POLARIZATION)


#     # Convert time to strain based on rate of micrometer motion
#     thick = 5.28  # thickness of the samples in mm
#     rate = 0.1  # rate of the micrometer (compression rate in mm/s)
#     strain = (timeList * rate) / thick
#     print(timeList)
#     print(strain)
#     print(phase)
#     print(s1List)
#     print(s2List)
#     return strain, phase
df = pd.read_csv("trial(Sheet1).csv")

# Extract columns into NumPy arrays
timeArr = df["time"].to_numpy()
s1Arr = df["Sdifference"].to_numpy()
s2Arr = np.zeros_like(s1Arr)  # Placeholder for S2
s3Arr = np.zeros_like(s1Arr)  # Placeholder for S3

d = DataAnalyzer()

# for i in range(len(s1Arr)):
#     # Assuming you have some logic to compute s2 and s3 based on s1
#     # Here we use dummy values for demonstration
#     prev_s3 = s3Arr[i-1] if i > 0 else None
#     s2Arr[i], s3Arr[i] = d.s2_s3_from_s1_angles(s1Arr[i], -.2007137, 1.15534, prev_s3)

d.write_stokes_csv(timeArr, s1Arr, .2007137, 1.15534, out_path="power_diff_for_matlab.csv")

pol = polarimeterCalibration
print("s1Arr: ", s1Arr)
print("s2Arr: ", s2Arr) 
print("s3Arr: ", s3Arr)
print("timeArr: ", timeArr) 

d.analyzeDataNoRealtime(s1Arr, s2Arr, s3Arr, timeArr)