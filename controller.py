import serial
import time

class Controller:
    def __init__(self):
        # Replace 'COM4' with the appropriate serial port identifier
        serialPort = 'COM3'
        self.micrometerPosition = 0.0

        # Replace the baudrate and other parameters with those specific to your Conex-CC controller
        baudRate = 921600
        parity = serial.PARITY_NONE
        stopBits = serial.STOPBITS_ONE
        dataBits = serial.EIGHTBITS

        try:
            # Open serial port
            self.ser = serial.Serial(serialPort, baudRate, parity=parity, stopbits=stopBits, bytesize=dataBits, timeout=1, xonxoff=True)
            print("Connected to", self.ser.name)
        except serial.SerialException as e:
            print("Serial connection error:", e)
            self.ser = None  # Set ser to None if the connection fails


    def getSerialPort(self): 
        return self.ser

    def goHome(self): 
        self.ser.write(b'1OR?\r\n')
        time.sleep(0.1)

    def disable(self):
        self.ser.write(b'1MM0\r\n')
        time.sleep(0.1)

    def checkError(self):
        checkError = "1" + "TE" + "\r\n"
        inBytes = bytes(checkError, 'utf-8')
        self.ser.write(inBytes)
        print(str(self.ser.readline()))

    def onQuit(self):
        self.ser.close()
        print("disconnected")

    def goToHeight(self, inputHeight, gui):
        positionCommand = "1" + "PA" + inputHeight + "\r\n"
        inBytes = bytes(positionCommand, 'utf-8')
        self.ser.write(inBytes)
        self.checkError()

        timeStamp = time.time()
        getPositionCommand = "1" + "TP" + "\r\n"
        inBytes = bytes(getPositionCommand, 'utf-8')
        if(float(self.micrometerPosition) < float(inputHeight)):
            while(float(self.micrometerPosition) <= float(inputHeight)):
                self.ser.write(inBytes)
                self.micrometerPosition = self.ser.readline()
                timeStamp = time.time()
                self.micrometerPosition = self.micrometerPosition.decode('utf-8')
                self.micrometerPosition = self.micrometerPosition[3:]
                self.micrometerPosition = float(self.micrometerPosition)
                gui.updateHeightLabel(self.micrometerPosition)
                time.sleep(0.1)
            print("done")

        if(float(self.micrometerPosition) > float(inputHeight)):
            while(float(self.micrometerPosition) >= float(inputHeight)):
                self.ser.write(inBytes)
                self.micrometerPosition = self.ser.readline()
                timeStamp = time.time()
                self.micrometerPosition = self.micrometerPosition.decode('utf-8')
                self.micrometerPosition = self.micrometerPosition[3:]
                self.micrometerPosition = float(self.micrometerPosition)
                gui.updateHeightLabel(self.micrometerPosition)
                time.sleep(0.1)
            print("done")
