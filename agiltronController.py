import serial
import time
import ConnectionFinder


class agiltronController:
    def __init__(self):
        self.port = 'COM3'
        self.baudrate = 9600
        self.ser = None
        self.posCommand = bytes([0x01, 0x16, 0x00, 0x00, 0x00, 0x00])
        self.checkVCommand = bytes([0x01, 0x18, 0x00, 0x00, 0x00, 0x00])
        self.setMaxVCommand = bytes([0x01, 0x17, 0x00, 0x00, 0x00, 0x00])
        self.running = False
        self.maxHeight = 120
        self.maxRaw = 700000
        self.currentPosition = 0.0
        # 2 raw counts in user units (~0.00034); positions this close count as "at" the target
        self.positionTolerance = 2 * self.maxHeight / self.maxRaw

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
        print("agiltronController.py - start called")
        # instantiate connection finder class
        finder = ConnectionFinder.ConnectionFinder()
        if not finder.check_platform():
            print("Warning: Running on unsupported platform.")
        finder.enumerate_all()
        finder.find_controller()

        if finder.port:
            self.port = finder.port
        # else:
        #     # auto-discovery failed — try fallback ports
        #     print("[ConnectionFinder] Auto-discovery returned no port.")
        #     print("[Fallback] Attempting fallback ports: COM5, COM3")
        #     for fallback in ['COM5', 'COM3']:
        #         print(f"[Fallback] Trying {fallback}...")
        #         self.port = fallback
        #         if self.openPort():
        #             print(f"[Fallback] Successfully connected on {fallback}")
        #             if run_loop:
        #                 self.runMainLoop()
        #             return True
        #         else:
        #             print(f"[Fallback] Failed to connect on {fallback}")
        #     print("[Error] Could not connect on any fallback port (COM5, COM3). Aborting.")
        #     return False

        # try opening port
        out = self.openPort()
        if not out:
            print(f"[Error] Failed to open discovered port {self.port}")
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
        print(f"Input a value between 0 and {self.maxHeight}:")
        userinput = float(input())
        return userinput

    def setPosition(self, pos):
        """Set the position of the controller."""
        # Scale input pos (0-maxHeight, may be fractional) to nearest raw count 0-maxRaw
        print(f"setPosition called at pos {pos}")
        scaled_pos = self.scale_int(pos)
        scaled_pos = max(0, min(self.maxRaw, scaled_pos))

        self.ser.flush() # wait for current output to finish
        self.ser.reset_output_buffer()
        bits_to_send = self.pos_to_bytes(scaled_pos)
        self.send_bits(bits_to_send)
        self.ser.flush() # wait for this output to finish

        print("Position set successfully")
        return True

    def goToHeight(self, pos, on_step=None, timeout=300):
        """Move to scaled position (0-maxHeight) and block until motion stabilizes.
        on_step(scaled) is invoked after each poll so observers (e.g. StageQueue) can sample.

        Stability alone is not treated as done, since the stage reads unchanged both before it
        starts moving and between counts at low speeds. Completion requires either:
          - reading within posTolerance raw counts of the target and stable for 5 polls, or
          - having moved at least once and stable for 20 polls (~1 s), for a stage that stops short.
        Gives up after timeout seconds. Returns True on completion, False on timeout."""

        target_raw = self.scale_int(pos)
        pos_tolerance = 100  # raw counts (~0.017 scaled units)
        self.setPosition(pos)
        stable_count = 0
        last_raw = None
        moved = False
        deadline = time.time() + timeout
        while True:
            if time.time() > deadline:
                print(f"[Warning] goToHeight({pos}) timed out after {timeout}s. Position: {self.currentPosition}")
                return False
            time.sleep(0.05)
            raw = self.getCurrentPos()
            if raw is None:
                continue
            # keep readback as a float: truncating to int made e.g. raw 5833 (pos 1) read back as 0
            scaled = self.scale(raw, 0, self.maxRaw, 0, self.maxHeight)
            self.currentPosition = scaled
            if on_step is not None:
                on_step(scaled)
            if last_raw is not None and raw == last_raw:
                stable_count += 1
            else:
                if last_raw is not None:
                    moved = True
                stable_count = 0
            last_raw = raw

            if abs(raw - target_raw) <= pos_tolerance and stable_count >= 5:
                break
            if moved and stable_count >= 20:
                print(f"[Warning] Stage settled {raw - target_raw} raw counts from target {target_raw}")
                break
        print(f"Movement complete. Position: {self.currentPosition}")
        return True

    def isAtPosition(self, pos):
        """True if currentPosition is within positionTolerance of pos (user units)."""
        return abs(self.currentPosition - pos) <= self.positionTolerance

    def goHome(self):
        """Move to position 0."""
        self.ser.flush()
        self.ser.reset_input_buffer()
        self.goToHeight(0)

    def setVelocity(self, speed):
        """Public alias for setMaxVelocity (0-100)."""
        self.ser.flush()
        print("Output Flushed")
        return self.setMaxVelocity(speed)

    def getCurrentPos(self):
        self.ser.reset_output_buffer()
        print("Output buffer reset")
        self.ser.reset_input_buffer()
        print("Input buffer reset")
        self.send_bits(self.posCommand)
        self.ser.flush()
        print("Output Flushed")

        response = self.ser.read(6)

        print(f"Received: {response.hex(' ')}, ", response)

        if len(response) < 6:
            print(f"Short read: got {len(response)} bytes")
            return None

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
        speed = self.scale_int(speed, 0, 100, 0, 250000000)

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
    def scale(self, value, in_min=0, in_max=None, out_min=0, out_max=None):
        """
        Linearly map value from [in_min, in_max] to [out_min, out_max] as a float.
        Defaults map 0-maxHeight (user units) to 0-maxRaw (device counts).
        """
        if in_max is None:
            in_max = self.maxHeight
        if out_max is None:
            out_max = self.maxRaw
        # lerp lerp lerp
        # lerp lerp
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def scale_int(self, value, in_min=0, in_max=None, out_min=0, out_max=None):
        """Same as scale(), rounded to the nearest integer (for values sent to the device)."""
        return int(round(self.scale(value, in_min, in_max, out_min, out_max)))

    def checkControllerConnection(self):
        out = ConnectionFinder.ConnectionFinder().find_silicon_labs_device()
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
