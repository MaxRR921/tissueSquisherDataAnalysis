




# """
# Example Application for PAX1000 Polarimeters in Python with CTypes

# Tested with Python 3.10.0 (64 bit)
# """

import os
import time
import ctypes
from ctypes import *
from threading import Thread, Lock
import dataAnalysisVmaster
import numpy as np
import controller

class Polarimeter():

    def __init__(self, micrometer):
        # Load DLL library
        self.micrometer = micrometer
        self.s1List = []
        self.s2List = []
        self.s3List = []
        self.timeList = []
        self.initTime = 0
        self.positionList = []
        self.lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")
        self.run = False
        # Detect and initialize PAX1000 device
        self.instrumentHandle = c_ulong()
        self.IDQuery = True
        self.resetDevice = False
        self.resource =  resource = create_string_buffer(256)
        self.deviceCount = c_int()

        # Check how many PAX1000 are connected
        self.lib.TLPAX_findRsrc(self.instrumentHandle, byref(self.deviceCount))
        if self.deviceCount.value < 1 :
            print("No PAX1000 device found.")
            exit()
        else:
            print(self.deviceCount.value, "PAX1000 device(s) found.")
            print("")

        # Connect to the first available PAX1000
        self.lib.TLPAX_getRsrcName(self.instrumentHandle, 0, self.resource)
        if (0 == self.lib.TLPAX_init(self.resource.value, self.IDQuery, self.resetDevice, byref(self.instrumentHandle))):
            print("Connection to first PAX1000 initialized.")
        else:
            print("Error with initialization.")
            exit()
        print("")

        # Short break to make sure the device is correctly initialized
        time.sleep(2)

        # Make settings
        self.lib.TLPAX_setMeasurementMode(self.instrumentHandle, 9)
        self.lib.TLPAX_setWavelength(self.instrumentHandle, c_double(633e-9))
        self.lib.TLPAX_setBasicScanRate(self.instrumentHandle, c_double(60))

        # Check settings
        wavelength = c_double()
        self.lib.TLPAX_getWavelength(self.instrumentHandle, byref(wavelength))
        print("Set wavelength [nm]: ", wavelength.value*1e9)
        mode = c_int()
        self.lib.TLPAX_getMeasurementMode(self.instrumentHandle, byref(mode))
        print("Set mode: ", mode.value)
        scanrate = c_double()
        self.lib.TLPAX_getBasicScanRate(self.instrumentHandle, byref(scanrate))
        print("Set scanrate: ", scanrate.value)
        print("")

        # Short break
        time.sleep(5)

        # Take 5 measurements and output values
        

    def start(self):
        self.s1List.clear()
        self.s2List.clear()
        self.s3List.clear()
        self.timeList.clear()
        self.positionList.clear()
        self.initTime = 0
        x = 0
        initTime = time.time()
        while self.run:
            revolutionCounter = c_int()
            scanID = c_int()
            self.lib.TLPAX_getLatestScan(self.instrumentHandle, byref(scanID))

            print("Measurement", (x+1))
            azimuth = c_double()
            ellipticity = c_double()
            s1 = c_double()
            s2 = c_double()
            s3 = c_double()
            self.lib.TLPAX_getPolarization(self.instrumentHandle, scanID.value, byref(azimuth), byref(ellipticity))
            self.lib.TLPAX_getStokesNormalized(self.instrumentHandle, scanID, byref(s1),byref(s2),byref(s3))
            print("Azimuth [rad]: ", azimuth.value)
            print("Ellipticity [rad]: ", ellipticity.value)
            print("s1: ", s1)
            print("s2: ", s2)
            print("s3: ", s3)
            self.s1List.append(s1.value)
            self.s2List.append(s2.value)
            self.s3List.append(s3.value)
            t = time.time()
            self.timeList.append(t - initTime)
            print("s1List: ", self.s1List)
            print("s2List: ", self.s2List)
            print("s3List: ", self.s3List)
           
            self.lib.TLPAX_releaseScan(self.instrumentHandle, scanID)
            try:
                self.positionList.append(self.micrometer.micrometerPosition.decode()[3:].strip())
                print(self.positionList)
            except:
                print("polarimeter reading of position data is invalid.")
                self.s1List.remove(s1.value)
                self.s2List.remove(s2.value)
                self.s3List.remove(s3.value)
                self.timeList.remove(t-initTime)
            time.sleep(0.5)

        # Close
        self.lib.TLPAX_close(self.instrumentHandle)
        print("Connection to PAX1000 closed.")



        self.instrumentHandle = c_ulong()
        self.IDQuery = True
        self.resetDevice = False
        self.resource =  resource = create_string_buffer(256)
        self.deviceCount = c_int()

        # Check how many PAX1000 are connected
        self.lib.TLPAX_findRsrc(self.instrumentHandle, byref(self.deviceCount))
        if self.deviceCount.value < 1 :
            print("No PAX1000 device found.")
            exit()
        else:
            print(self.deviceCount.value, "PAX1000 device(s) found.")
            print("")

        # Connect to the first available PAX1000
        self.lib.TLPAX_getRsrcName(self.instrumentHandle, 0, self.resource)
        if (0 == self.lib.TLPAX_init(self.resource.value, self.IDQuery, self.resetDevice, byref(self.instrumentHandle))):
            print("Connection to first PAX1000 initialized.")
        else:
            print("Error with initialization.")
            exit()
        print("")

        # Short break to make sure the device is correctly initialized
        time.sleep(2)

        # Make settings
        self.lib.TLPAX_setMeasurementMode(self.instrumentHandle, 9)
        self.lib.TLPAX_setWavelength(self.instrumentHandle, c_double(633e-9))
        self.lib.TLPAX_setBasicScanRate(self.instrumentHandle, c_double(60))

        # Check settings
        wavelength = c_double()
        self.lib.TLPAX_getWavelength(self.instrumentHandle, byref(wavelength))
        print("Set wavelength [nm]: ", wavelength.value*1e9)
        mode = c_int()
        self.lib.TLPAX_getMeasurementMode(self.instrumentHandle, byref(mode))
        print("Set mode: ", mode.value)
        scanrate = c_double()
        self.lib.TLPAX_getBasicScanRate(self.instrumentHandle, byref(scanrate))
        print("Set scanrate: ", scanrate.value)
        print("")

        # Short break
        time.sleep(1)

        # Take 5 measurements and output values
        print("Polarimter thread should close here...")
        self.run = True

    def stop(self):
        self.run = False
        print("POLARIMETER STOPPING")
        self.lib.TLPAX_close(self.instrumentHandle)