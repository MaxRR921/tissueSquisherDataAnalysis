# Use of Ophir COM object. 
# Works with python 3.5.1 & 2.7.11
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
            OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
            # Stop & Close all devices
            OphirCOM.StopAllStreams() 
            OphirCOM.CloseAll()
            # Scan for connected Devices
            deviceList =  OphirCOM.ScanUSB()
            print( deviceList)
            # if any device is connected
            print("bar")
            # there are two devices
            # power1 = Thread(target =  __collectData, args=[ deviceList[0]])
            # power2 = Thread(target=  __collectData, args=[ deviceList[1]])

            # power1.start()
            # power2.start()
            # power1.join()
            # power2.join()

            for device in  deviceList:
                deviceHandle =  OphirCOM.OpenUSBdevice(device)# open first device
                exists =  OphirCOM.IsSensorExists(deviceHandle, 0)
                print("collectdata runs")
                if exists:
                    print('\n----------Data for S/N {0} ---------------'.format(device))
                    # An Example for data retrieving
                    OphirCOM.StartStream(deviceHandle, 0)# start measuring
                    for i in range(10):
                        time.sleep(.2)# wait a little for data
                        data =  OphirCOM.GetData(deviceHandle, 0)
                        if len(data[0]) > 0: # if any data available, print the first one from the batch
                            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))

                else:
                    print('\nNo Sensor attached to {0} !!!'.format(device))
            
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            traceback.print_exc()

        win32gui.MessageBox(0, 'finished', '', 0)
        # Stop & Close all devices
        OphirCOM.StopAllStreams()
        OphirCOM.CloseAll()
        # Release the object
        OphirCOM = None



    def __collectData(self, device):
        deviceHandle = self.OphirCOM.OpenUSBdevice(device)# open first device
        exists = self.OphirCOM.IsSensorExists(deviceHandle, 0)
        print("collectdata runs")
        if exists:
            print('\n----------Data for S/N {0} ---------------'.format(device))
            # An Example for data retrieving
            self.OphirCOM.StartStream(deviceHandle, 0)# start measuring
            for i in range(10):
                time.sleep(.2)# wait a little for data
                data = self.OphirCOM.GetData(deviceHandle, 0)
                if len(data[0]) > 0: # if any data available, print the first one from the batch
                    print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))

        else:
            print('\nNo Sensor attached to {0} !!!'.format(device))
