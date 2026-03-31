import subprocess
import glob
import json
import re
import platform
import contextlib
import os
from typing import Dict, List, Any


class ConnectionFinder:
    """Class for finding and enumerating serial port connections."""

    def __init__(self):
        self.port = ""
        self.system = platform.system()

    # ------------------------------------------------------------------ #
    #  Platform detection                                                  #
    # ------------------------------------------------------------------ #

    def get_platform(self) -> str:
        """Return the current platform: 'Darwin', 'Windows', or 'Linux'."""
        return self.system

    def check_platform(self) -> bool:
        """
        Check that the current platform is supported.
        Returns True if supported (Darwin or Windows), False otherwise.
        """
        supported = ['Darwin', 'Windows']
        if self.system not in supported:
            print(f"Warning: Platform '{self.system}' is not fully supported.")
            print(f"Supported platforms: {', '.join(supported)}")
            return False
        print(f"Platform detected: {self.system}")
        return True

    # ------------------------------------------------------------------ #
    #  TTY / Serial port discovery                                         #
    # ------------------------------------------------------------------ #

    def list_tty_devices(self) -> list:
        """Lists all /dev/tty.* devices via glob."""
        try:
            devices = glob.glob('/dev/tty.*')
            return sorted(devices)
        except Exception as e:
            print(f"Error listing TTY devices: {e}")
            return []

    def list_tty_devices_shell(self) -> list:
        """Lists all /dev/tty.* devices via shell ls."""
        try:
            result = subprocess.run(
                ['ls', '/dev/tty.*'],
                capture_output=True,
                text=True,
                check=True
            )
            devices = result.stdout.strip().split('\n')
            return [d for d in devices if d]
        except subprocess.CalledProcessError as e:
            print(f"No TTY devices found or error: {e}")
            return []
        except Exception as e:
            print(f"Error running shell command: {e}")
            return []

    def find_slab_controller(self):
        """Searches device list for a Silicon Labs USB-to-UART connection."""
        devices = self.list_tty_devices()
        print("Searching device list...")
        for device in devices:
            if device[-4:] == 'UART':
                print("Silicon Labs USB to UART Connection Found!")
                self.port = device
                print("Port: ", self.port)
            else:
                continue

    # ------------------------------------------------------------------ #
    #  macOS device enumeration helpers                                    #
    # ------------------------------------------------------------------ #

    def _run_command(self, cmd: List[str]) -> str:
        """Execute a shell command and return stdout."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"

    def enumerate_ioreg_usb(self) -> List[Dict[str, Any]]:
        """Parse USB devices using ioreg."""
        print("\n" + "=" * 60)
        print("USB DEVICES (via ioreg)")
        print("=" * 60)

        output = self._run_command(['ioreg', '-p', 'IOUSB', '-w0', '-l'])

        devices = []
        current_device = {}

        for line in output.split('\n'):
            if '+-o' in line and '@' in line:
                if current_device:
                    devices.append(current_device)
                match = re.search(r'\+-o\s+([^@<]+)', line)
                if match:
                    current_device = {'name': match.group(1).strip()}

            if current_device and '"' in line:
                if 'idVendor' in line:
                    match = re.search(r'idVendor"\s*=\s*(\d+)', line)
                    if match:
                        current_device['vendor_id'] = match.group(1)

                if 'idProduct' in line:
                    match = re.search(r'idProduct"\s*=\s*(\d+)', line)
                    if match:
                        current_device['product_id'] = match.group(1)

                if 'USB Serial Number' in line:
                    match = re.search(r'"USB Serial Number"\s*=\s*"([^"]+)"', line)
                    if match:
                        current_device['serial'] = match.group(1)

                if '"Speed"' in line:
                    match = re.search(r'"Speed"\s*=\s*"([^"]+)"', line)
                    if match:
                        current_device['speed'] = match.group(1)

        if current_device:
            devices.append(current_device)

        for i, dev in enumerate(devices, 1):
            print(f"\n{i}. {dev.get('name', 'Unknown')}")
            if 'vendor_id' in dev:
                print(f"   Vendor ID: {dev['vendor_id']}")
            if 'product_id' in dev:
                print(f"   Product ID: {dev['product_id']}")
            if 'serial' in dev:
                print(f"   Serial: {dev['serial']}")
            if 'speed' in dev:
                print(f"   Speed: {dev['speed']}")

        return devices

    def enumerate_system_profiler_usb(self):
        """List USB devices using system_profiler."""
        print("\n" + "=" * 60)
        print("USB DEVICES (via system_profiler)")
        print("=" * 60)

        output = self._run_command(['system_profiler', 'SPUSBDataType', '-json'])

        try:
            data = json.loads(output)
            usb_data = data.get('SPUSBDataType', [])

            def print_usb_tree(items, indent=0):
                for item in items:
                    name = item.get('_name', 'Unknown')
                    print("  " * indent + f"• {name}")
                    if 'vendor_id' in item:
                        print("  " * indent + f"  Vendor ID: {item['vendor_id']}")
                    if 'product_id' in item:
                        print("  " * indent + f"  Product ID: {item['product_id']}")
                    if 'serial_num' in item:
                        print("  " * indent + f"  Serial: {item['serial_num']}")
                    if '_items' in item:
                        print_usb_tree(item['_items'], indent + 1)

            print_usb_tree(usb_data)

        except json.JSONDecodeError:
            print("Could not parse system_profiler output")

    def enumerate_thunderbolt(self):
        """List Thunderbolt devices."""
        print("\n" + "=" * 60)
        print("THUNDERBOLT DEVICES")
        print("=" * 60)

        output = self._run_command(['system_profiler', 'SPThunderboltDataType'])

        if "No Thunderbolt" in output or not output.strip():
            print("No Thunderbolt devices found")
        else:
            print(output)

    def enumerate_storage(self):
        """List storage/disk devices."""
        print("\n" + "=" * 60)
        print("STORAGE DEVICES")
        print("=" * 60)

        output = self._run_command(['diskutil', 'list'])
        print(output)

    def enumerate_network_interfaces(self):
        """List network interfaces (including USB ethernet adapters)."""
        print("\n" + "=" * 60)
        print("NETWORK INTERFACES")
        print("=" * 60)

        output = self._run_command(['networksetup', '-listallhardwareports'])
        print(output)

    def enumerate_pyusb(self):
        """List USB devices via PyUSB if available."""
        print("\n" + "=" * 60)
        print("USB DEVICES (via PyUSB)")
        print("=" * 60)

        try:
            import usb.core
            import usb.util

            devices = list(usb.core.find(find_all=True))

            if not devices:
                print("No devices found via PyUSB")
                return

            for i, dev in enumerate(devices, 1):
                print(f"\n{i}. Device {dev.idVendor:04x}:{dev.idProduct:04x}")
                print(f"   Vendor ID: 0x{dev.idVendor:04x} ({dev.idVendor})")
                print(f"   Product ID: 0x{dev.idProduct:04x} ({dev.idProduct})")
                try:
                    if dev.manufacturer:
                        print(f"   Manufacturer: {dev.manufacturer}")
                    if dev.product:
                        print(f"   Product: {dev.product}")
                    if dev.serial_number:
                        print(f"   Serial: {dev.serial_number}")
                except Exception:
                    pass
                print(f"   Bus: {dev.bus}, Address: {dev.address}")

        except ImportError:
            print("PyUSB not installed. Install with: pip3 install pyusb")
            print("Note: PyUSB also requires libusb: brew install libusb")

    def find_silicon_labs_device(self) -> list:
        """Find CP2102N devices via PyUSB and map to serial port."""
        try:
            import usb.core
            import usb.util
        except ImportError:
            print("PyUSB not installed. Install with: pip3 install pyusb")
            print("Note: PyUSB also requires libusb: brew install libusb")
            return []

        SILICON_LABS_VID = 0x10C4
        CP2102N_PID = 0xEA60

        usb_devices = usb.core.find(find_all=True, idVendor=SILICON_LABS_VID, idProduct=CP2102N_PID)

        devices = []
        for dev in usb_devices:
            device_info = {
                'name': 'CP2102N USB to UART Bridge Controller',
                'vendor_id': f"0x{dev.idVendor:04x}",
                'product_id': f"0x{dev.idProduct:04x}",
                'bus': dev.bus,
                'address': dev.address
            }

            try:
                if dev.manufacturer:
                    device_info['manufacturer'] = dev.manufacturer
                if dev.product:
                    device_info['product'] = dev.product
                if dev.serial_number:
                    device_info['serial'] = dev.serial_number
            except Exception:
                pass

            tty_devices = self.list_tty_devices()
            for port in tty_devices:
                if 'SLAB' in port:
                    device_info['port'] = port
                    break

            devices.append(device_info)

        for dev in devices:
            print(f"\nFound CP2102N Device (via PyUSB):")
            print(f"  Name: {dev.get('name', 'Unknown')}")
            print(f"  Vendor ID: {dev.get('vendor_id', 'Unknown')}")
            print(f"  Product ID: {dev.get('product_id', 'Unknown')}")
            if 'manufacturer' in dev:
                print(f"  Manufacturer: {dev['manufacturer']}")
            if 'product' in dev:
                print(f"  Product: {dev['product']}")
            if 'serial' in dev:
                print(f"  Serial: {dev['serial']}")
            print(f"  Bus: {dev.get('bus', 'Unknown')}, Address: {dev.get('address', 'Unknown')}")
            if 'port' in dev:
                print(f"  Port: {dev['port']}")

        return devices

    # ------------------------------------------------------------------ #
    #  Windows device enumeration helpers                                  #
    # ------------------------------------------------------------------ #

    def list_com_ports(self) -> list:
        """List available COM ports using pyserial's list_ports."""
        try:
            from serial.tools import list_ports
            ports = list(list_ports.comports())
            return ports
        except ImportError:
            print("pyserial not installed. Install with: pip install pyserial")
            return []

    def enumerate_com_ports(self) -> List[Dict[str, Any]]:
        """Enumerate COM ports with detailed info (Windows)."""
        print("\n" + "=" * 60)
        print("COM PORTS (via pyserial)")
        print("=" * 60)

        ports = self.list_com_ports()
        devices = []

        for port in ports:
            device_info = {
                'device': port.device,
                'name': port.description,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid,
                'serial_number': port.serial_number,
                'manufacturer': port.manufacturer,
            }
            devices.append(device_info)

            print(f"\n  Port: {port.device}")
            print(f"  Description: {port.description}")
            print(f"  HWID: {port.hwid}")
            if port.vid is not None:
                print(f"  Vendor ID: 0x{port.vid:04x}")
            if port.pid is not None:
                print(f"  Product ID: 0x{port.pid:04x}")
            if port.serial_number:
                print(f"  Serial: {port.serial_number}")
            if port.manufacturer:
                print(f"  Manufacturer: {port.manufacturer}")

        if not devices:
            print("No COM ports found.")

        return devices

    def enumerate_wmi_usb(self) -> List[Dict[str, Any]]:
        """Enumerate USB devices via PowerShell/WMI (Windows only)."""
        print("\n" + "=" * 60)
        print("USB DEVICES (via WMI)")
        print("=" * 60)

        if self.system != 'Windows':
            print("WMI enumeration is only available on Windows.")
            return []

        cmd = [
            'powershell', '-Command',
            'Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq "Ports" -or $_.PNPClass -eq "USB" } '
            '| Select-Object Name, DeviceID, Manufacturer, PNPClass '
            '| ConvertTo-Json'
        ]

        output = self._run_command(cmd)
        devices = []

        try:
            data = json.loads(output)
            # PowerShell returns a single object (not list) if only one result
            if isinstance(data, dict):
                data = [data]

            for item in data:
                device_info = {
                    'name': item.get('Name', 'Unknown'),
                    'device_id': item.get('DeviceID', ''),
                    'manufacturer': item.get('Manufacturer', ''),
                    'pnp_class': item.get('PNPClass', ''),
                }
                devices.append(device_info)

                print(f"\n  Name: {device_info['name']}")
                print(f"  Device ID: {device_info['device_id']}")
                if device_info['manufacturer']:
                    print(f"  Manufacturer: {device_info['manufacturer']}")
                print(f"  Class: {device_info['pnp_class']}")

        except (json.JSONDecodeError, TypeError):
            print("Could not parse WMI output")

        return devices

    def find_slab_controller_windows(self):
        """Search COM ports for a Silicon Labs USB-to-UART connection (Windows)."""
        ports = self.list_com_ports()
        print("Searching COM ports for Silicon Labs device...")

        SILICON_LABS_VID = 0x10C4

        for port in ports:
            if port.vid == SILICON_LABS_VID or 'Silicon Labs' in (port.description or ''):
                print(f"Silicon Labs USB to UART Connection Found!")
                self.port = port.device
                print(f"Port: {self.port}")
                return

            if 'CP210' in (port.description or ''):
                print(f"CP210x device found!")
                self.port = port.device
                print(f"Port: {self.port}")
                return

        print("No Silicon Labs device found on COM ports.")

    # ------------------------------------------------------------------ #
    #  Cross-platform discovery                                            #
    # ------------------------------------------------------------------ #

    def find_controller(self):
        """Find the Silicon Labs controller on the current platform."""
        self.check_platform()
        if self.system == 'Darwin':
            self.find_slab_controller()
        elif self.system == 'Windows':
            self.find_slab_controller_windows()
        else:
            print(f"No device discovery method for platform: {self.system}")

    def enumerate_all(self, verbose=False):
        """Run all device enumeration methods for the current platform."""
        if self.system == 'Darwin':
            self.enumerate_all_mac(verbose=verbose)
        elif self.system == 'Windows':
            self.enumerate_all_windows(verbose=verbose)
        else:
            print(f"No enumeration methods available for platform: {self.system}")

    # ------------------------------------------------------------------ #
    #  Windows full enumeration                                            #
    # ------------------------------------------------------------------ #

    def enumerate_all_windows(self, verbose=False):
        """
        Run all Windows device enumeration methods.
        Only executes on Windows; no-op on other platforms.
        Pass verbose=True to print output; silent by default when imported.
        """
        if self.system != 'Windows':
            return

        sink = open(os.devnull, 'w')
        ctx = contextlib.nullcontext() if verbose else contextlib.redirect_stdout(sink)

        with ctx:
            if verbose:
                print("\n" + "=" * 60)
                print("WINDOWS DEVICE ENUMERATION")
                print("=" * 60)

            self.enumerate_com_ports()
            self.enumerate_wmi_usb()

            if verbose:
                print("\n" + "=" * 60)
                print("ENUMERATION COMPLETE")
                print("=" * 60)

        if not verbose:
            sink.close()

    # ------------------------------------------------------------------ #
    #  macOS full enumeration                                              #
    # ------------------------------------------------------------------ #

    def enumerate_all_mac(self, verbose=False):
        """
        Run all device enumeration methods.
        Only executes on macOS (Darwin); no-op on other platforms.
        Pass verbose=True to print output; silent by default when imported.
        """
        if platform.system() != 'Darwin':
            return

        sink = open(os.devnull, 'w')
        ctx = contextlib.nullcontext() if verbose else contextlib.redirect_stdout(sink)

        with ctx:
            if verbose:
                print("\n" + "=" * 60)
                print("MAC DEVICE ENUMERATION")
                print("=" * 60)

            self.enumerate_ioreg_usb()
            self.enumerate_system_profiler_usb()
            self.enumerate_pyusb()
            self.enumerate_thunderbolt()
            self.enumerate_storage()
            self.enumerate_network_interfaces()

            if verbose:
                print("\n" + "=" * 60)
                print("ENUMERATION COMPLETE")
                print("=" * 60)

        if not verbose:
            sink.close()


if __name__ == "__main__":
    finder = ConnectionFinder()
    finder.check_platform()
    finder.enumerate_all(verbose=True)
    finder.find_controller()
