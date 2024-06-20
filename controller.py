import serial
import time
from plotter import Plot2D
import tkinter as tk
#NOTE: EACH COMMAND SENT TO THE CONTROLLER TAKES ABOUT 10 ms from command sent to result returned to computer. (for error)

class Controller:
    def __init__(self):
        self.root = tk._default_root
        #self.plot = Plot2D('micrometer plot', 'time', 'distance')
        # Replace 'COM1' with the appropriate serial port identifier
        serialPort = 'COM3'
        self.micrometerPosition = 0.0
        self.timeStamp = 0.0
        self.updating = True

        #port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, 
        #stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
        # Replace the baudrate and other parameters with those specific to your Conex-CC controller
        baudRate = 921600
        parity = serial.PARITY_NONE
        stopBits = serial.STOPBITS_ONE
        dataBits = serial.EIGHTBITS

        #self.root.after(100, self.updatePlotFromData)
        
        

        try:
            # Open serial port
            self.ser = serial.Serial(serialPort, baudRate, parity=parity, stopbits=stopBits, bytesize=dataBits, timeout=1, xonxoff=True)
            print("Connected to", self.ser.name)
            
            # Close serial port
            # ser.close()
            # print("Disconnected")
        except serial.SerialException as e:
            print("Serial connection error:", e)

    def getSerialPort(self): 
        return self.ser

    def goHome(self): 
        self.ser.write(b'1OR?\r\n')
        time.sleep(0.1)

    def setHome(self):
        self.ser.write(b'1HT1')
        time.sleep(0.1)
        self.ser.write(b'1HT?')
        time.sleep(1)
        print("ERROR:")
        self.checkError()

    def disable(self):
        self.ser.write(b'1MM0\r\n')
        #readResponse(ser.readline().decode().strip())
        time.sleep(0.1)

    def checkError(self):
        checkError = "1" + "TE" + "\r\n"
        inBytes = bytes(checkError, 'utf-8')
        self.ser.write(inBytes)
        print(str(self.ser.readline()))

    def onQuit(self):
        self.ser.close()
        print("disconnected")

    def goToHeight(self, inputHeight):
        
        #send command to go to position
        positionCommand = "1" + "PA" + inputHeight + "\r\n"
        inBytes = bytes(positionCommand, 'utf-8')
        self.ser.write(inBytes)

        
        timeStamp = time.time()
        getPositionCommand = "1" + "TP" + "\r\n"
        inBytes = bytes(getPositionCommand, 'utf-8')
        if(float(self.micrometerPosition) < float(inputHeight)):
            while(float(self.micrometerPosition) <= float(inputHeight)):
                self.ser.write(inBytes)
                self.micrometerPosition = self.ser.readline()
                self.timeStamp = time.time()
                self.micrometerPosition = self.micrometerPosition.decode('utf-8')
                self.micrometerPosition = self.micrometerPosition[3:]
                float(self.micrometerPosition)
                time.sleep(0.1)
            print("done")

        if(float(self.micrometerPosition) > float(inputHeight)):
            while(float(self.micrometerPosition) >= float(inputHeight)):
                self.ser.write(inBytes)
                self.micrometerPosition = self.ser.readline()
                self.timeStamp = time.time() 
                self.micrometerPosition = self.micrometerPosition.decode('utf-8')
                self.micrometerPosition = self.micrometerPosition[3:]
                float(self.micrometerPosition)
                time.sleep(0.1)
            print("done")
        
    
    def readResponse(self, response):                                                                                                                                    
        print(str(response))

    