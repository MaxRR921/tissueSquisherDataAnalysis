# Uses pywin32
import win32gui
import win32com.client
import pythoncom
import time
import traceback
from threading import Thread
class Powermeter:

    def start(self):
        pythoncom.CoInitialize()
        print("hello")
        try:
            self.OphirCom = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
            # Stop & Close all devices
            self.OphirCom.StopAllStreams() 
            self.OphirCom.CloseAll()
            # Scan for connected Devices
            self.deviceList = self.OphirCom.ScanUSB()
            print(self.deviceList[0])
            print(self.deviceList[1])
            # if any device is connected
            
            power1 = Thread(target = self.__runDevice1, args=[self.deviceList[0]])
            power2 = Thread(target = self.__runDevice2, args=[self.deviceList[1]])
            power1.start()
            power2.start()
            power1.join()
            power2.join()


            
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            traceback.print_exc()
        win32gui.MessageBox(0, 'finished', '', 0)
        # Stop & Close all devices
        self.OphirCom.StopAllStreams()
        self.OphirCom.CloseAll()
        # Release the object
        self.OphirCom = None




    def __runDevices(self):
        for device in self.deviceList:   
            
            deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
            exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
            if exists:
                print('\n----------Data for S/N {0} ---------------'.format(device))
                # An Example for data retrieving
                self.OphirCom.StartStream(deviceHandle, 0)# start measuring
                for i in range(10):
                    time.sleep(.2)# wait a little for data
                    data = self.OphirCom.GetData(deviceHandle, 0)
                    if len(data[0]) > 0: # if any data available, print the first one from the batch
                        print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
            else:
                print('\nNo Sensor attached to {0} !!!'.format(device))




    def __runDevice1(self, device):
        deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
        exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
        if exists:
            print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCom.StartStream(deviceHandle, 0)# start measuring
            for i in range(10):
                time.sleep(.2)# wait a little for data
                data = self.OphirCom.GetData(deviceHandle, 0)
                if len(data[0]) > 0: # if any data available, print the first one from the batch
                    print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))


    def __runDevice2(self, device):
        deviceHandle = self.OphirCom.OpenUSBDevice(device)# open first device
        exists = self.OphirCom.IsSensorExists(deviceHandle, 0)
        if exists:
            print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCom.StartStream(deviceHandle, 0)# start measuring
            for i in range(10):
                time.sleep(.2)# wait a little for data
                data = self.OphirCom.GetData(deviceHandle, 0)
                if len(data[0]) > 0: # if any data available, print the first one from the batch
                    print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))