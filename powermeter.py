# Uses pywin32
"""checks to see if the modules can be imported. on mac win32 can't be imported so we can't use this device on a macbook."""
try:
    # import win32gui
    import win32com.client
    import pythoncom
except ImportError:
    print("win32 modules are not available on this platform. Continuing without them.")

import time
import threading
import numpy as np
import queue
import multiprocessing

###IMPORTANT!!! THREADS FOR EAHC POWERMETER SHARE A COMMON RUN VARIABLE BEWARE OF RACE CONDITIONS BUT DOESN"T MATTER BC
###ITS ALWAYS TRUE RIGHT NOW.


class Powermeter:
    """init initializes the connection to the devices using python com device, then uses win32com to get the OphirLMMeasurement (powermeter)
    device on initialize it stops all data coming from the devices and closes them then scans the usb ports for devices and adds them to our
    list of devices. There should be two devices connected because of our dual powermeter measurement system
    
    !!want to add ability to just use one device without the program breaking
    !TRY except blocks here are a little misleading because if there is one device connected it will give a module
    not found error even though it's just a memory address unavailable.

    initializes the device times to zero and sets .run to true by default !!(this seems weird, i guess we are constantly polling from these 
    devices even when we aren't trying to take measurements which i guess is good for seeing results even when nothing is happening.)
    """
    def __init__(self):
        try:
            pythoncom.CoInitialize()
            self.OphirCom = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
            # Stop & Close all devices
            self.OphirCom.StopAllStreams() 
            self.OphirCom.CloseAll()
            # Scan for connected Devices
            self.deviceList = self.OphirCom.ScanUSB()
            print(self.deviceList[0])
            print(self.deviceList[1])
            # if any device is connected    
            self.device1ZeroTime = 0.0
            self.device2ZeroTime = 0.0
            self.device1Data = 0.0
            self.device2Data = 0.0
            self.device1CsvQueue = queue.Queue()
            self.device2CsvQueue = queue.Queue()
            self.device1PlotQueue = multiprocessing.Queue()
            self.device2PlotQueue = multiprocessing.Queue()
            self.updatingDevice1PlotQueue = threading.Event()
            self.updatingDevice2PlotQueue = threading.Event()
            self.updatingDevice1CsvQueue = threading.Event()
            self.updatingDevice2CsvQueue = threading.Event()

            self.run = threading.Event()
            self.run.set()  # to start running
        except OSError as err:
            print("OS error: {0}".format(err))
        except ModuleNotFoundError as e:
            print("Module not found error:", e)
        except:
            print("no powermeters connected. Note: you must be on windows.")
        # Stop & Close all devices


    """start creates one thread for each powermeter device that should be connected. it's in a try catch block incase two devices are connected
    or there is an error, but !!I want to make it so one device could be connected...?"""
    def start(self):
        try:
            power1 = threading.Thread(target = self.__runDevice1, args=[self.deviceList[0]])
            power2 = threading.Thread(target = self.__runDevice2, args=[self.deviceList[1]])
            power1.start()
            power2.start()
            power1.join()
            power2.join()
            #self.__printData()
            self.OphirCom.StopAllStreams()
            self.OphirCom.CloseAll()
            print("RELEASED")
            # Release the object
            self.OphirCom = None
        except IndexError as e:
            print(f"An error occurred: {e}")

    def __runDevice1(self, device):
        i=0
        deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
        exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
        if exists:
            # print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCom.StartStream(deviceHandle, 0)# start measuring
            while self.run.is_set():  
                time.sleep(.2)# wait a little for data
                data = self.OphirCom.GetData(deviceHandle, 0)
                if len(data[0]) > 0: # if any data available, print the first one from the batch
                    # print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
                    # print(time.time())
                    if(i==0):
                        self.device1ZeroTime = data[1][0]
                        deltaTime = 0   
                    else:
                        deltaTime = data[1][0] - self.device1ZeroTime

                    newData = np.array([[data[0][0], deltaTime, data[2][0]]])
                    #self.device1Data = np.append(self.device1Data, newData, axis=0) 
                    self.device1Data = data[0][0]
                    if(self.updatingDevice1CsvQueue.is_set()):
                        self.device1CsvQueue.put(float(data[0][0]))
                    if(self.updatingDevice1PlotQueue.is_set()):
                        self.device1PlotQueue.put(float(data[0][0]))
                        print("PUTTING!!!!")
                    # print("DATA:", self.device1Data)
                i=i+1


                   
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))


    def __runDevice2(self, device):
        i=0
        deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
        exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
        if exists:
            # print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCom.StartStream(deviceHandle, 0)# start measuring
            while self.run.is_set():
                time.sleep(.2)# wait a little for data
                data = self.OphirCom.GetData(deviceHandle, 0)
                if len(data[0]) > 0: # if any data available, print the first one from the batch
                    # print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
                    # print(time.time())
                    if(i==0):
                        self.device2ZeroTime = data[1][0]
                        deltaTime = 0   
                    else:
                        deltaTime = data[1][0] - self.device2ZeroTime

                    newData = np.array([[data[0][0], deltaTime, data[2][0]]])
                    self.device2Data = data[0][0]
                    if(self.updatingDevice2CsvQueue.is_set()):
                        self.device2CsvQueue.put(data[0][0])
                    if(self.updatingDevice2PlotQueue.is_set()):
                        self.device2PlotQueue.put(data[0][0])
                    # print("DATA:", self.device2Data)
                i=i+1
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))

    def stop(self):
        self.run.clear()

    def __printData(self):
        print('\n----------Data for S/N {0} ---------------'.format(self.deviceList[0]))
        for reading in self.device1Data:
            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(reading[0], reading[1], reading[2]))
        print('\n----------Data for S/N {0} ---------------'.format(self.deviceList[1]))
        for reading in self.device2Data:
            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(reading[0], reading[1], reading[2]))
