import serial
import time



class Controller:
    def __init__(self):
        # Replace 'COM1' with the appropriate serial port identifier
        serialPort = 'COM4'


        #port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, 
        #stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
        # Replace the baudrate and other parameters with those specific to your Conex-CC controller
        baudRate = 921600
        parity = serial.PARITY_NONE
        stopBits = serial.STOPBITS_ONE
        dataBits = serial.EIGHTBITS
        

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
        #readResponse(ser.readline().decode().strip())
        time.sleep(0.1)


    def disable(self):
        self.ser.write(b'1MM0\r\n')
        #readResponse(ser.readline().decode().strip())
        time.sleep(0.1)

    def checkError(self):
        checkError = "1" + "TE" + "\r\n"
        inBytes = bytes(checkError, 'utf-8')
        self.ser.write(inBytes)
        return str(self.ser.readline())

    def onQuit(self):
        self.ser.close()
        print("disconnected")

    def goToHeight(self, inputHeight):
        ts1 = time.time()
        positionCommand = "1" + "PA" + inputHeight + "\r\n"
        inBytes = bytes(positionCommand, 'utf-8')
        self.ser.write(inBytes)
        time.sleep(5)
        checkError = "1" + "TE" + "\r\n"
        inBytes = bytes(checkError, 'utf-8')
        self.ser.write(inBytes)
        return str(self.ser.readline())
    
        micrometerPosition = 0


        timeStamp = time.time()
        getPositionCommand = "1" + "TP" + "\r\n"
        inBytes = bytes(positionCommand, 'utf-8')
        self.ser.write(inBytes)
        print(self.ser.readline())
        self.checkError()


        time.sleep(0.1)
        ts2 = time.time()

    def readResponse(self, response):
        print(str(response))

    