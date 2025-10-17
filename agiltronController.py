import serial
import time

class agiltronController:
    def __init__(self):
        self.port = '/dev/cu.SLAB_USBtoUART'
        self.baudrate = 9600
        self.ser = None
        self.posCommand = bytes([0x01, 0x16, 0x00, 0x00, 0x00, 0x00])


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
            self.ser.write(data)
            print(f"Sent data: {data}")
            return True
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False

    # take position in mm
    # does not work
    '''
    def calculate_bytes(self, position):
        byte1 = position / 65536
        byte2 = position / 256
        byte3 = position
        return byte1, byte2, byte3
    '''

    # ! Working !
    def pos_to_bytes(self,pos):
        byte0 = pos // 65536
        byte1 = (pos % 65536) // 256
        byte2 = pos % 256
        return bytes([0x01, 0x14, 0x00, byte0, byte1, byte2])


if __name__ == '__main__':
    # Create instance of controller
    controller = agiltronController()

    # Example of sending some test data
    test_pos = 10
    data = controller.pos_to_bytes(test_pos)
    data = data[:-1]  # Remove last byte
    # Result: b'\x01\x14\x00\x00\x00'

    print(data)

    # controller.openPort()



    try:
        # Send the test data
        # controller.send_bits(controller.posCommand)

        # response = controller.ser.read(6)
        # print(f"Received: {response.hex(' ')}")

        # controller.send_bits(controller.pos_to_bytes(16))
        #  ensure data is sent
        time.sleep(1)


    finally:
        # close port
        controller.closePort()
