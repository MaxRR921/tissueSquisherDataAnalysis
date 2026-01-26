import serial
import time
import enumerateDevices as enumerate
import ConnectionFinder


class agiltronController:
    def __init__(self):
        self.port = ''
        self.baudrate = 9600
        self.ser = None
        self.posCommand = bytes([0x01, 0x16, 0x00, 0x00, 0x00, 0x00])
        self.checkVCommand = bytes([0x01, 0x18, 0x00, 0x00, 0x00, 0x00])
        self.setMaxVCommand = bytes([0x01, 0x17, 0x00, 0x00, 0x00, 0x00])
        self.running = False

    def openPort(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.3)  # allow opening
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
    def pos_to_bytes(self, pos):
        byte0 = pos // 65536
        byte1 = (pos % 65536) // 256
        byte2 = pos % 256

        print("Input position as integer: ", pos)

        out_bytes = bytes([0x01, 0x14, 0x00, byte0, byte1, byte2])
        print("Output of pos_to_bytes: ", out_bytes)

        return out_bytes

    def speed_to_bytes(self, speed):
        """Convert a 32-bit speed value to 4 bytes for max velocity command."""
        byte0 = (speed >> 24) & 0xFF
        byte1 = (speed >> 16) & 0xFF
        byte2 = (speed >> 8) & 0xFF
        byte3 = speed & 0xFF

        print("Input speed as integer: ", speed)

        out_bytes = bytes([0x01, 0x17, byte0, byte1, byte2, byte3])
        print("Output of speed_to_bytes: ", out_bytes)

        return out_bytes

    def start(self, run_loop=True):
        # instantiate connection finder class
        finder = ConnectionFinder.ConnectionFinder()
        finder.find_slab_controller()
        self.port = finder.port

        # try opening port
        out = self.openPort()
        if not out:
            return False
        else:
            print("Connection to port established")
            if run_loop:
                self.runMainLoop()
            return True

    def runMainLoop(self):
        time.sleep(0.5)
        self.running = True
        user_input = ""
        while self.running:
            print("Input desired action (1 = setpos, 2 = getpos, 3 = setmaxv, 4 = checkmaxv, exit) : ")
            user_input = input()

            if user_input == "exit":
                self.closePort()
                print("Exiting program...")
                break

            if user_input == "1":
                pos = self.getUserInputPos()
                self.setPosition(pos)

            if user_input == "2":
                self.getCurrentPos()

            if user_input == "3":
                speed = self.getInputSpeed()
                self.setMaxVelocity(speed)

            if user_input == "4":
                self.checkMaxVelocity()

    def getUserInputPos(self):
        print("Input a value between 0 and 50:")
        userinput = int(input())
        return userinput

    def setPosition(self, pos):
        """Set the position of the controller."""
        # Scale input pos to 0-700000
        # scale_int scales from 0-50 to 0-700000 by default
        scaled_pos = self.scale_int(pos)

        bits_to_send = self.pos_to_bytes(scaled_pos)
        self.send_bits(bits_to_send)

        print("Position set successfully")
        return True

    def getCurrentPos(self):
        self.send_bits(self.posCommand)
        response = self.ser.read(6)

        print(f"Received: {response.hex(' ')}, ", response)

        pos = int.from_bytes(response[3:6], byteorder='big')
        print("Position as int:", pos)
        return pos

    def checkMaxVelocity(self):
        self.send_bits(self.checkVCommand)
        response = self.ser.read(6)

        print("Received: ", response.hex(' '))
        maxVelocity = int.from_bytes(response[2:6], byteorder='big') # fixed to correctly receive bytes
        print("Max velocity is: ", maxVelocity)
        return maxVelocity

    def setMaxVelocity(self, speed):
        """Set the maximum velocity of the controller."""
        #scale to input, takes in 0-100 and outputs safe values
        speed = self.scale_int(speed, 0, 100, 75000000, 240000000)

        bits_to_send = self.speed_to_bytes(speed)
        print(bits_to_send)
        self.send_bits(bits_to_send)
        response = self.ser.read(6)

        print("Received: ", response.hex(' '))
        print("Max velocity set successfully")
        return True

    def getInputSpeed(self):
        print("Input desired max velocity (as integer):")
        userinput = int(input())
        return userinput



    # claude generated ahh function 😭
    def scale_int(self, value, in_min=0, in_max=50, out_min=0, out_max=700000):
        """
        Scale an integer from one range to another.
        Args:
            value: Input value to scale
            in_min: Minimum of input range (default 0)
            in_max: Maximum of input range (default 50)
            out_min: Minimum of output range (default 0)
            out_max: Maximum of output range (default 700000)

        Returns:
            Scaled integer value
        """
        # lerp lerp lerp
        # lerp lerp
        # Linear interpolation formula
        scaled = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        return int(scaled)

    def checkControllerConnection(self):
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

if __name__ == '__main__':
    # Create instance of controller
    controller = agiltronController()

    # controller.checkControllerConnection()

    if not controller.start():
        print("Controller could not start.")
        exit()
