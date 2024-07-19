# """
# Example Application for PAX1000 Polarimeters in Python with CTypes

# Tested with Python 3.10.0 (64 bit)
# """

import os
import time
import ctypes
from ctypes import *
from threading import Thread
import dataAnalysisVmaster
import numpy as np

class Polarimeter():


    def __init__(self):
        self.s1List = []
        self.s2List = []
        self.s3List = []
        self.timeList = []
        self.phaseList = []
        self.strainList = []



    def start(self, numIterations):
        try:
            #load dll library
            lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")


        # Detect and initialize PAX1000 device
            instrumentHandle = c_ulong()
            IDQuery = True
            resetDevice = False
            resource = c_char_p(b"")
            deviceCount = c_int()


            # Check how many PAX1000 are connected
            lib.TLPAX_findRsrc(instrumentHandle, byref(deviceCount))

            if deviceCount.value < 1 :
                print("No PAX1000 device found.")
                exit()
            else:
                print(deviceCount.value, "PAX1000 device(s) found.")


            # # Connect to the first available PAX1000
            print("INSTRUMENT HANDLE BEFORE IS ", instrumentHandle.value)
            lib.TLPAX_getRsrcName(instrumentHandle, 0, resource)
            if (0 == lib.TLPAX_init(resource.value, IDQuery, resetDevice, byref(instrumentHandle))):
                print("Connection to first PAX1000 initialized.")
            else:
                print("Error with initialization.")
                exit()
            print("")
            print("INSTRUMENT HANDLE IS", instrumentHandle.value)


            # # Short break to make sure the device is correctly initialized
            time.sleep(.5)


            # # Make settings
            lib.TLPAX_setMeasurementMode(instrumentHandle, 9)
            lib.TLPAX_setBasicScanRate(instrumentHandle, c_double(60))

            # Check settings
            wavelength = c_double()
            lib.TLPAX_getWavelength(instrumentHandle, byref(wavelength))
            print("Set wavelength [nm]: ", wavelength.value*1e9)
            mode = c_int()
            lib.TLPAX_getMeasurementMode(instrumentHandle, byref(mode))
            print("Set mode: ", mode.value)
            scanrate = c_double()
            lib.TLPAX_getBasicScanRate(instrumentHandle, byref(scanrate))
            print("Set scanrate: ", scanrate.value)
            print("")

            # Short break
            time.sleep(.1)

            initTime = time.time()
            for x in range (numIterations):
               
                print("print numiteration is")
                print(numIterations)
                revolutionCounter = c_int()
                scanID = c_int()
                print("SCAN ID IS BEFORE", scanID.value)
                lib.TLPAX_getLatestScan(instrumentHandle, byref(scanID))
                print("SCAN ID IS", scanID.value)
                print("Measurement", (x+1))
                azimuth = c_double()
                ellipticity = c_double()
                try:
                    s1 = c_double()
                    s2 = c_double()
                    s3 = c_double()
                    timeStamp = c_uint32()
                    lib.TLPAX_getTimeStamp(instrumentHandle, scanID, byref(timeStamp))
                    print("TIMESTAMP IS: ", timeStamp.value)
                    vi = lib.TLPAX_getStokesNormalized(instrumentHandle, scanID, byref(s1),byref(s2),byref(s3))
                    print("VI STATUS IS: ", vi)
                    print("S1 Normalized: ", s1.value)
                    print("S2 Normalized: ", s2.value)
                    print("S3 Normalized: ", s3.value)
                    print("")
                    lib.TLPAX_releaseScan(instrumentHandle, scanID)
                    # dataAnalyzer.analyzeData(s1.value, s2.value, s3.value, timeStamp.value)
                    self.s1List.append(s1.value)
                    self.s2List.append(s3.value)
                    self.s3List.append(s3.value)
                    self.timeList.append(time.time() - initTime)

                    

                    time.sleep(.01)
                except:
                    print("doesn't work here")
            # Close
            lib.TLPAX_close(instrumentHandle)
            print("Connection to PAX1000 closed.")
        except:
            print("no polarimeter connected")


    def analyzeData(self):
        print("hello")
