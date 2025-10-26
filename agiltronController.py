import serial
import time

class agiltronController:
    def __init__(self):
        self.port = '/dev/cu.SLAB_USBtoUART'
        self.baudrate = 9600
        self.ser = None
        self.posCommand = bytes([0x01, 0x16, 0x00, 0x00, 0x00, 0x00])
        self.running = False


    def openPort(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.3) # allow opening
            print("Port opened")
            return True
        except serial.SerialException as e:
            print("Serial connection error:", e)
            return False

    def closePort(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Port closed")

    def send_bits(self, data):
        if not self.ser or not self.ser.is_open:
            print("Port not open. Opening port...")
            if not self.openPort():
                return False
        try:
            # show exact bytes that will be written
            print("Writing bytes (hex):", data.hex(' '))
            self.ser.write(data)
            try:
                self.ser.flush()
            except Exception:
                pass
            print(f"Sent data: {data} ({data.hex(' ')})")
            return True
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False

    # ! Working !
    def pos_to_bytes(self,pos):
        byte0 = pos // 65536
        byte1 = (pos % 65536) // 256
        byte2 = pos % 256

        print("Input position as integer: ", pos)

        out_bytes = bytes([0x01, 0x14, 0x00, byte0, byte1, byte2])
        print("Output of pos_to_bytes: ",  out_bytes)

        return out_bytes

    def start(self):
        out = self.openPort()
        if out == False:
            return
        else:
            print("connection to port established")
            self.closePort()
            self.runMainLoop()


    def runMainLoop(self):
        time.sleep(0.5)
        self.running = True;
        user_input = "";
        while self.running:
            print("Input desired action (1 = setpos, 2 = getpos, exit) : ")
            user_input = input()

            if (user_input == "exit"):
                print("Exiting program...")
                break

            if user_input == "1":
                self.openPort()
                bits_to_send = self.pos_to_bytes(self.getInputPos())
                self.send_bits(bits_to_send)
                self.closePort()

    def getInputPos(self):
        print("Input a value between 0 and 50:")
        userinput = int(input())
        return userinput

    def getCurrentPos(self):
        


if __name__ == '__main__':
    # Create instance of controller
    controller = agiltronController()

    controller.start()
