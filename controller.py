import serial
import time




def initialize(): 
   # Replace 'COM1' with the appropriate serial port identifier
    serialPort = '/dev/cu.usbserial-FT82MKCO'


    #port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, 
    #stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
    # Replace the baudrate and other parameters with those specific to your Conex-CC controller
    baudRate = 921600
    parity = serial.PARITY_NONE
    stopBits = serial.STOPBITS_ONE
    dataBits = serial.EIGHTBITS
    

    try:
        # Open serial port
        ser = serial.Serial(serialPort, baudRate, parity=parity, stopbits=stopBits, bytesize=dataBits, timeout=1, xonxoff=True)
        print("Connected to", ser.name)
        
        # Close serial port
        # ser.close()
        # print("Disconnected")
    except serial.SerialException as e:
        print("Serial connection error:", e)
        
    return ser

def goHome(ser): 
    ser.write(b'1OR?\r\n')
    #readResponse(ser.readline().decode().strip())
    time.sleep(0.1)


def disable(ser):
    ser.write(b'1MM0\r\n')
    #readResponse(ser.readline().decode().strip())
    time.sleep(0.1)


def onQuit(ser):
    ser.close()
    print("disconnected")


def readResponse(response):
    print(str(response))

def goToHeight(inp, ser):
    ts1 = time.time()
    theStr = "1" + "PA" + inp + "\r\n"
    print(theStr)
    inBytes = bytes(theStr, 'utf-8')
    print(str(inBytes))
    ser.write(inBytes)
    time.sleep(0.1)
    ts2 = time.time()
   

