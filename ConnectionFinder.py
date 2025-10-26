import subprocess
import glob


class ConnectionFinder:
    """Class for finding available serial port connections."""

    def __init__(self):
        self.port = ""

    def list_tty_devices(self):
        """
        Lists all available /dev/tty.* devices.

        Returns:
            list: A list of device paths that match /dev/tty.*
        """
        try:
            # Use glob to find all matching devices
            devices = glob.glob('/dev/tty.*')
            return sorted(devices)
        except Exception as e:
            print(f"Error listing TTY devices: {e}")
            return []

    def list_tty_devices_shell(self):
        """
        Lists all available /dev/tty.* devices using shell command.

        Returns:
            list: A list of device paths that match /dev/tty.*
        """
        try:
            result = subprocess.run(
                ['ls', '/dev/tty.*'],
                capture_output=True,
                text=True,
                check=True
            )
            devices = result.stdout.strip().split('\n')
            return [d for d in devices if d]  # Filter out empty strings
        except subprocess.CalledProcessError as e:
            # ls returns error if no matches found
            print(f"No TTY devices found or error: {e}")
            return []
        except Exception as e:
            print(f"Error running shell command: {e}")
            return []

    def find_slab_controller(self):
        devices = self.list_tty_devices()
        print("Searching device list...")
        # print(devices)
        for device in devices:
            # print(device[-4:])
            if device[-4:] == 'UART':
                print("Silicon Labs USB to UART Connection Found! ")
                self.port = device
                print("Port: ", self.port)
            else:
                continue


if __name__ == "__main__":
    finder = ConnectionFinder()
    finder.find_slab_controller()
    # devices = finder.list_tty_devices()
    # print("Available TTY devices:")
    # for device in devices:
        # print(device)
