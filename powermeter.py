# Uses pywin32
try:
    # import win32gui
    import win32com.client
    import pythoncom
except ImportError:
    print("win32 modules are not available on this platform. Continuing without them.")

import time
import traceback
from threading import Thread
import numpy as np
class Powermeter:
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
            self.plot = True
        except OSError as err:
            print("OS error: {0}".format(err))
        except ModuleNotFoundError as e:
            print("Module not found error:", e)
        except:
            print("no powermeters connected. Note: you must be on windows.")
        # Stop & Close all devices
        thread = Thread(target = self.start, args=[])
        thread.start()

    def start(self):
        try:
            power1 = Thread(target = self.__runDevice1, args=[self.deviceList[0]])
            power2 = Thread(target = self.__runDevice2, args=[self.deviceList[1]])
            power1.start()
            power2.start()
            power1.join()
            power2.join()
            #self.__printData()
            self.OphirCom.StopAllStreams()
            self.OphirCom.CloseAll()
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
            while(self.plot == True):
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
                i=i+1


                   
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))


    def __runDevice2(self, device):
        deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
        exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
        if exists:
            # print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCom.StartStream(deviceHandle, 0)# start measuring
            for i in range(300):
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
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))


    def __printData(self):
        print('\n----------Data for S/N {0} ---------------'.format(self.deviceList[0]))
        for reading in self.device1Data:
            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(reading[0], reading[1], reading[2]))
        print('\n----------Data for S/N {0} ---------------'.format(self.deviceList[1]))
        for reading in self.device2Data:
            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(reading[0], reading[1], reading[2]))
