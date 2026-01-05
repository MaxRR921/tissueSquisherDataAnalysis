import serial
import time
import tkinter as tk
import threading
import queue
import multiprocessing
import enumerateDevices as enumerate
import ConnectionFinder
#NOTE: EACH COMMAND SENT TO THE CONTROLLER TAKES ABOUT 10 ms from command sent to result returned to computer. (for error)
"""new branch"""
class Controller:
    """init sets the usb serial settings for the micrometer controller, telling what port it should be in 
    !!!! add dynamic port checking so that you don't have to manually go into the code and change the port to the right
    port number for your computer. I think the try catch here is fine because it just tries to open the serial port and if it fails it
    throws an exception. I'm thinking for this sort of thing we should just quit the program because why are you ever even running if you 
    don't have a micrometer or two powermeters connected. the polarimeter stuff will probably be deleted eventually """
    def __init__(self):
        self.root = tk._default_root # _default_root is a private variable pointing to the *default* root window created on tkinter import
        #self.plot = Plot2D('micrometer plot', 'time', 'distance')
        # Replace 'COM1' with the appropriate serial port identifier
        serialPort = 'COM4'
        self.micrometerPosition = b'0'
        self.timeStamp = 0.0
        self.updating = True
        self.lastInputHeight = 0
        self.downward = False
        #port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, 
        #stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
        # Replace the baudrate and other parameters with those specific to your Conex-CC controller
        baudRate = 921600
        parity = serial.PARITY_NONE
        stopBits = serial.STOPBITS_ONE
        dataBits = serial.EIGHTBITS
        self.updatingCsvQueue = threading.Event()
        self.updatingCsvQueue.clear()
        self.csvQueue = queue.Queue()
        self.updatingPlotQueue = threading.Event()
        self.updatingPlotQueue.clear()
        self.plotQueue = multiprocessing.Queue()

        # Agiltron controller attributes
        self.agiltronPort = ''
        self.agiltronBaudrate = 9600
        self.agiltronSer = None
        self.posCommand = bytes([0x01, 0x16, 0x00, 0x00, 0x00, 0x00])
        self.checkVCommand = bytes([0x01, 0x18, 0x00, 0x00, 0x00, 0x00])
        self.setMaxVCommand = bytes([0x01, 0x17, 0x00, 0x00, 0x00, 0x00])
        self.agiltronRunning = False

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
        self.goHome()

    """getSerialPort retuns the ser variable so it can be accessed from other classes"""
    def getSerialPort(self): 
        return self.ser

    """goHome writes the serial command to tell the micrometer to go to it's currently set home position, which 
    is zero by default. NOTE: you can change this by issuing the PW command which make's the controller's display light
    blink red. You can only use this command to write to the controller's nonvolatile memory around 100 times so use sparingly but it might 
    be a good thing to change the home position in the future so you don't have to raise t up to set up an experiment every time"""
    def goHome(self): 
        try:
            self.ser.write(b'1OR?\r\n')
            print("RUNS")
            time.sleep(0.1)
        except AttributeError as e:
            print("Serial connection error:", e)
        
    """enterTracking writes the tracking mode command to the micrometer which makes it constantly track it's current position 
    !!!Add try except to this """
    def enterTracking(self):
        self.ser.write(b'1TK0\r\n')
        time.sleep(0.1)

    """setVelocity writes the command to set the controller's velocity !ADD TRY EXCEPT Not sure why it also asks for the velocity and then writes
    what it asks too!!!!!!"""
    def setVelocity(self, inputVelocity):
        print("input is")
        print(inputVelocity)
        velocityCommand = "1" + "VA" + inputVelocity + "\r\n"
        inBytes = bytes(velocityCommand, 'utf-8')
        self.ser.write(inBytes)
        velocityCommand = "1" + "VA" + "?" + "\r\n"
        inBytes = bytes(velocityCommand, 'utf-8')
        self.ser.write(inBytes)

    """disable writes the command to the controller to enter the disable state, which only allows a limited subset of commands to be executed
    excluding movement commands. !ADD TRY EXCEPT"""
    def disable(self):
        self.ser.write(b'1MM0\r\n')
        #readResponse(ser.readline().decode().strip())
        time.sleep(0.1)

    """checkError writes the command to the controller to check for the last error that occurred and was written to it's nonvolatile memory 
    !ADD EXCEPTION HANDLING"""
    def checkError(self):
        checkError = "1" + "TE" + "\r\n"
        inBytes = bytes(checkError, 'utf-8')
        self.ser.write(inBytes)
        print(str(self.ser.readline()))

    """onQuit  closes the connection to the serial port, !ADD TRY except"""
    def onQuit(self):
        self.ser.close()
        print("disconnected")


    """invert input takes in an input string and inverts it."""
    def invertHeight(self, num_str):
        try:
            num = float(num_str)  # Convert to float to handle decimals
            if 0 <= num <= 12:
                return str(12 - num)  # Convert back to string
            else:
                raise ValueError("Number must be between 0 and 12")
        except ValueError:
            raise ValueError("Invalid input: must be a number between 0 and 12")

    """goToHeight takes in an input height and writes the command to the controller to got o that height
    for some reason i'm doing all this other bs here too but i'm too scared to change it right now 
    !TODO: look into this. LOOK INTO THIS LATER"""
    def goToHeight(self, inputHeight): #polling rate is pretty consistently .03 - .04 seconds = 30 miliseconds as of 3/13/2025

        inputHeight = self.invertHeight(inputHeight) 

        positionCommand = "1" + "PA" + inputHeight + "\r\n"
        inBytes = bytes(positionCommand, 'utf-8')
        self.ser.write(inBytes)

        
        timeStamp = time.time()
        getStateCommand = "1" + "TS" + "\r\n"
        inBytes = bytes(getStateCommand, 'utf-8')
        compare = b'1TS000028\r\n'
        self.ser.write(b'1TS\r\n')\
        #no idea why but for some reason you need to read twice and on the second time you will get the command look into this later.
        self.ser.readline()
        state = self.ser.readline()
        print(state)
        while(state == compare):
            print("RUNS")
            getPositionCommand = "1" + "TP" + "\r\n"
            inBytes = bytes(getPositionCommand, 'utf-8')
            self.ser.write(inBytes)
            self.micrometerPosition = self.ser.readline()
            if(self.updatingCsvQueue.is_set()):
                self.csvQueue.put((float(self.micrometerPosition[3:].strip()), time.time()))
            if(self.updatingPlotQueue.is_set()):
                x = 12 - float(self.micrometerPosition[3:].strip())
                print("XINCONTROLLER: ", x)
                self.plotQueue.put((time.time(), x))
            # print(self.micrometerPosition)
            self.timeStamp = time.time()
            self.ser.write(b'1TS\r\n')
            state = self.ser.readline()
           
            
        print("done")
    

    """testCommand issues the command to test if commands are working i don't think i use this anywhere !TODO: add try except """
    def testCommand(self):
        testCommand = "1" + "TS" + "\r\n"
        inBytes = bytes(testCommand, 'utf-8')
        self.ser.write(inBytes)
        returned = self.ser.readline()
        print(returned)

        

    """readResponse takes in a response from the controller given to it by the user, then turns it into a string using python str(), and prints it"""
    def readResponse(self, response):                                                                                                                                    
        print(str(response))

    """stop disables the controller !TODO(WHY NOT CALL DISABLE?????)"""
    def stop(self):
        self.disable()

    # Agiltron controller methods
    def agiltronOpenPort(self):
        try:
            self.agiltronSer = serial.Serial(self.agiltronPort, self.agiltronBaudrate, timeout=1)
            time.sleep(0.3)
            print("Port opened")
            return True
        except serial.SerialException as e:
            print("Serial connection error:", e)
            return False

    def agiltronClosePort(self):
        if self.agiltronSer and self.agiltronSer.is_open:
            self.agiltronSer.close()
            print("Port closed")

    def agiltronSendBits(self, data):
        if not self.agiltronSer or not self.agiltronSer.is_open:
            print("Port not open. Opening port...")
            if not self.agiltronOpenPort():
                return False
        try:
            print("Writing bytes (hex):", data.hex(' '))
            self.agiltronSer.write(data)
            try:
                self.agiltronSer.flush()
            except Exception:
                pass
            print(f"Sent data: {data} ({data.hex(' ')})")
            return True
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False

    def agiltronPosToBytes(self, pos):
        byte0 = pos // 65536
        byte1 = (pos % 65536) // 256
        byte2 = pos % 256
        print("Input position as integer: ", pos)
        out_bytes = bytes([0x01, 0x14, 0x00, byte0, byte1, byte2])
        print("Output of pos_to_bytes: ", out_bytes)
        return out_bytes

    def agiltronSpeedToBytes(self, speed):
        byte0 = (speed >> 24) & 0xFF
        byte1 = (speed >> 16) & 0xFF
        byte2 = (speed >> 8) & 0xFF
        byte3 = speed & 0xFF
        print("Input speed as integer: ", speed)
        out_bytes = bytes([0x01, 0x17, byte0, byte1, byte2, byte3])
        print("Output of speed_to_bytes: ", out_bytes)
        return out_bytes

    def agiltronStart(self):
        finder = ConnectionFinder.ConnectionFinder()
        finder.find_slab_controller()
        self.agiltronPort = finder.port
        out = self.agiltronOpenPort()
        if not out:
            return False
        else:
            print("Connection to port established")
            self.agiltronRunMainLoop()
            return True

    def agiltronRunMainLoop(self):
        time.sleep(0.5)
        self.agiltronRunning = True
        user_input = ""
        while self.agiltronRunning:
            print("Input desired action (1 = setpos, 2 = getpos, 3 = setmaxv, 4 = checkmaxv, exit) : ")
            user_input = input()
            if user_input == "exit":
                self.agiltronClosePort()
                print("Exiting program...")
                break
            if user_input == "1":
                pos = self.agiltronGetInputPos()
                pos = self.agiltronScaleInt(pos)
                bits_to_send = self.agiltronPosToBytes(pos)
                self.agiltronSendBits(bits_to_send)
            if user_input == "2":
                self.agiltronGetCurrentPos()
            if user_input == "3":
                speed = self.agiltronGetInputSpeed()
                self.agiltronSetMaxVelocity(speed)
            if user_input == "4":
                self.agiltronCheckMaxVelocity()

    def agiltronGetInputPos(self):
        print("Input a value between 0 and 50:")
        userinput = int(input())
        return userinput

    def agiltronGetCurrentPos(self):
        self.agiltronSendBits(self.posCommand)
        response = self.agiltronSer.read(6)
        print(f"Received: {response.hex(' ')}, ", response)
        pos = int.from_bytes(response[3:6], byteorder='big')
        print("Position as int:", pos)
        return pos

    def agiltronCheckMaxVelocity(self):
        self.agiltronSendBits(self.checkVCommand)
        response = self.agiltronSer.read(6)
        print("Received: ", response.hex(' '))
        maxVelocity = int.from_bytes(response[3:6], byteorder='big')
        print("Max velocity is: ", maxVelocity)
        return maxVelocity

    def agiltronSetMaxVelocity(self, speed):
        bits_to_send = self.agiltronSpeedToBytes(speed)
        self.agiltronSendBits(bits_to_send)
        response = self.agiltronSer.read(6)
        print("Received: ", response.hex(' '))
        print("Max velocity set successfully")
        return True

    def agiltronGetInputSpeed(self):
        print("Input desired max velocity (as integer):")
        userinput = int(input())
        return userinput

    def agiltronScaleInt(self, value, in_min=0, in_max=50, out_min=0, out_max=700000):
        scaled = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        return int(scaled)

    def agiltronCheckControllerConnection(self):
        out = enumerate.find_silicon_labs_device()
        if out is []:
            print("Device could not be found.")
            return False
        else:
            print("Device found: ")
            for key, value in out[0].items():
                if key == 'name':
                    print(value)
            return True

    def agiltronGoToPosition(self, pos):
        scaled_pos = self.agiltronScaleInt(pos)
        bits_to_send = self.agiltronPosToBytes(scaled_pos)
        self.agiltronSendBits(bits_to_send)
