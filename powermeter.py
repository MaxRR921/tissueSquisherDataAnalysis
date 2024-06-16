# Uses pywin32
import win32gui
import win32com.client
import pythoncom
import time
import traceback

class PowerMeter:

    def start(self):
        pythoncom.CoInitialize()
        print("hello")
        try:
            OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
            # Stop & Close all devices
            OphirCOM.StopAllStreams() 
            OphirCOM.CloseAll()
            # Scan for connected Devices
            DeviceList = OphirCOM.ScanUSB()
            print(DeviceList)
            # if any device is connected
            for Device in DeviceList:   
            
                DeviceHandle = OphirCOM.OpenUSBDevice(Device)# open first device
                exists = OphirCOM.IsSensorExists(DeviceHandle, 0)
                if exists:
                    print('\n----------Data for S/N {0} ---------------'.format(Device))
                    # An Example for data retrieving
                    OphirCOM.StartStream(DeviceHandle, 0)# start measuring
                    for i in range(10):
                        time.sleep(.2)# wait a little for data
                        data = OphirCOM.GetData(DeviceHandle, 0)
                        if len(data[0]) > 0: # if any data available, print the first one from the batch
                            print('Reading = {0}, TimeStamp = {1}, Status = {2} '.format(data[0][0] ,data[1][0] ,data[2][0]))
                else:
                    print('\nNo Sensor attached to {0} !!!'.format(Device))
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