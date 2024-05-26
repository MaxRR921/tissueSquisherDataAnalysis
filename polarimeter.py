# """
# Example Application for PAX1000 Polarimeters in Python with CTypes

# Tested with Python 3.10.0 (64 bit)
# """

import os
import time
import ctypes
from ctypes import *
def test():
# # Load DLL library
    lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")

    #CHECK FUNCTIONS
    dll_path = "C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll"
    if os.path.exists(dll_path):
        pax1000_dll = ctypes.CDLL(dll_path)
        print(f"Loaded DLL: {dll_path}")

        # List the functions in the DLL
        function_list = [func for func in dir(pax1000_dll) if not func.startswith('_')]
        print("Functions in the DLL:")
        for func in function_list:
            print(func)
    else:
        print(f"Error: DLL not found at {dll_path}")

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
    #     print("")

    # # Connect to the first available PAX1000
    lib.TLPAX_getRsrcName(instrumentHandle, 0, resource)
    if (0 == lib.TLPAX_init(resource.value, IDQuery, resetDevice, byref(instrumentHandle))):
        print("Connection to first PAX1000 initialized.")
    else:
        print("Error with initialization.")
        exit()
    print("")

    # # Short break to make sure the device is correctly initialized
    time.sleep(2)


    # # Make settings
    # lib.TLPAX_setMeasurementMode(instrumentHandle, 9)
    # lib.TLPAX_setWavelength(instrumentHandle, c_double(633e-9))
    # lib.TLPAX_setBasicScanRate(instrumentHandle, c_double(60))

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
    #time.sleep(5)

    #Take 5 measurements and output values
    for x in range (5):
        revolutionCounter = c_int()
        scanID = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle, byref(scanID))
        lib.TLPAX
        print("SCAN ID IS", scanID.value)
        print("Measurement", (x+1))
        azimuth = c_double()
        ellipticity = c_double()
        print(lib.TLPAX_getPolarization(instrumentHandle))
        print("Azimuth [rad]: ", azimuth.value)
        print("Ellipticity [rad]: ", ellipticity.value)
        print("")

        lib.TLPAX_releaseScan(instrumentHandle, scanID)
        time.sleep(0.5)

    # Close
    lib.TLPAX_close(instrumentHandle)
    print("Connection to PAX1000 closed.")