import time
from ctypes import *
import threading 
import queue 
import dataAnalysisVmaster

class Polarimeter():


    """init takes in a reference to the micrometer class so that it can track the position for the plotting
     initializes three lists for the stokes parameters, as well as a list for the positions. loads the drivers for the polarimeter.
     initializes and detects polarimeter, connects and sets the settings that are appropriate for the stress sensor. This class takes a break after
     initializing, and the main gui class waits for it to finish initializing to make sure that all settings are initialized before the program moves 
     on."""
    def __init__(self, micrometer):
        # Load DLL library
        self.micrometer = micrometer
        self.updatingCsvQueue = threading.Event()
        self.updatingCsvQueue.clear()
        self.s1Queue = queue.Queue()
        self.s2Queue = queue.Queue()
        self.s3Queue = queue.Queue()
        self.timeQueue = queue.Queue()
        self.initTime = 0
        #you need to have a windows machine because that's the only one that can have this driver. this line loads this from the default
        #path this driver is installed in on your machine
        self.lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")
        self.run = False
        # Detect and initialize PAX1000 device
        self.instrumentHandle = c_ulong()
        self.IDQuery = True
        self.resetDevice = False
        self.resource =  resource = create_string_buffer(256)
        self.deviceCount = c_int()
        self.dataAnalyzer = dataAnalysisVmaster.DataAnalyzer()

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

        
    """start runs on collect() in gui class. starts by clearing all of the object's lists while the self.run bool is set 
    (set to true from the gui class in collect), it gets the measurement data every .1 seconds as well as the timestamp associated 
    with this measurement data. I tried getting the time associated with the measurement from the polarimeter, but that was causing weird
    problems and wouldn't work. Might be a good idea in the future especially considering a !!!!! number of probably lengthy instructions
    occur before the time is recorded, so that could be a SOURCE OF ERROR in experiment 
      
    !! when self.run is set to false in the gui class (probably bad practice, because it's unclear here when the while loop will terminate)
    After the while loop terminates and while the data is being processed by the analysis class, it closes and reinitializes the connection with the 
    polarimeter !might be able to run init() again rather than duplicating the initialization code here.  
    """
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
            # print("Azimuth [rad]: ", azimuth.value)
            # print("Ellipticity [rad]: ", ellipticity.value)
            # print("s1: ", s1)
            # print("s2: ", s2)
            # print("s3: ", s3)
            self.s1Queue.put(s1.value)
            self.s2Queue.put(s2.value)
            self.s3Queue.put(s3.value)
            self.timeQueue.put(c_double(time.time() - initTime))
            self.lib.TLPAX_releaseScan(self.instrumentHandle, scanID)
            time.sleep(0.1)
        
        print("ANALYZING DATA !!! !!! !! ")
        self.dataAnalyzer.analyzeData(self.s1Queue, self.s2Queue, self.s3Queue, self.timeQueue)

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

    """!!stop sets the run flag to false, so the polarimeter breaks out of the loop and then reinitializes itself... 
    maybe don't want to reinitialize but idk i think it needs to because we want to be able to run again"""
    def stop(self):
        self.run = False
        print("POLARIMETER STOPPING")
        self.lib.TLPAX_close(self.instrumentHandle)