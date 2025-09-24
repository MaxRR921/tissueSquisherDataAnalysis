import serial
import time

class agiltronController:
    def __init__(self):
        self.port = 'COM3'
        self.baudrate = 9600

    def openPort(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.3) # allow opening
            print("Port opened")

        except serial.SerialException as e:
            print("Serial connection error:", e)
