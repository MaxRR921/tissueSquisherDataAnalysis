#!/usr/bin/env python3
"""
Comprehensive Mac Device Enumerator
Lists all USB, USB-C, Thunderbolt, and other connected devices

REQUIREMENTS
PyUSB - pip3 install pyusb
libusb - brew install libusb
"""

import subprocess
import json
import re
from typing import Dict, List, Any


def run_command(cmd: List[str]) -> str:
    """Execute a shell command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


def parse_ioreg_usb() -> List[Dict[str, Any]]:
    """Parse USB devices using ioreg"""
    print("\n" + "=" * 60)
    print("USB DEVICES (via ioreg)")
    print("=" * 60)

    output = run_command(['ioreg', '-p', 'IOUSB', '-w0', '-l'])

    devices = []
    current_device = {}

    for line in output.split('\n'):
        # Look for device entries
        if '+-o' in line and '@' in line:
            if current_device:
                devices.append(current_device)
            # Extract device name
            match = re.search(r'\+-o\s+([^@<]+)', line)
            if match:
                current_device = {'name': match.group(1).strip()}

        # Extract properties
        if current_device and '"' in line:
            # Vendor ID
            if 'idVendor' in line:
                match = re.search(r'idVendor"\s*=\s*(\d+)', line)
                if match:
                    current_device['vendor_id'] = match.group(1)

            # Product ID
            if 'idProduct' in line:
                match = re.search(r'idProduct"\s*=\s*(\d+)', line)
                if match:
                    current_device['product_id'] = match.group(1)

            # Serial Number
            if 'USB Serial Number' in line:
                match = re.search(r'"USB Serial Number"\s*=\s*"([^"]+)"', line)
                if match:
                    current_device['serial'] = match.group(1)

            # Speed
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


def list_usb_system_profiler():
    """List USB devices using system_profiler"""
    print("\n" + "=" * 60)
    print("USB DEVICES (via system_profiler)")
    print("=" * 60)

    output = run_command(['system_profiler', 'SPUSBDataType', '-json'])

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
                if 'Media' in item:
                    print("  " * indent + f"  Type: {', '.join(item['Media'])}")

                if '_items' in item:
                    print_usb_tree(item['_items'], indent + 1)

        print_usb_tree(usb_data)

    except json.JSONDecodeError:
        print("Could not parse system_profiler output")


def list_thunderbolt_devices():
    """List Thunderbolt devices"""
    print("\n" + "=" * 60)
    print("THUNDERBOLT DEVICES")
    print("=" * 60)

    output = run_command(['system_profiler', 'SPThunderboltDataType'])

    if "No Thunderbolt" in output or not output.strip():
        print("No Thunderbolt devices found")
    else:
        print(output)


def list_storage_devices():
    """List storage/disk devices"""
    print("\n" + "=" * 60)
    print("STORAGE DEVICES")
    print("=" * 60)

    output = run_command(['diskutil', 'list'])
    print(output)


def list_network_interfaces():
    """List network interfaces (including USB ethernet adapters)"""
    print("\n" + "=" * 60)
    print("NETWORK INTERFACES")
    print("=" * 60)

    output = run_command(['networksetup', '-listallhardwareports'])
    print(output)


def check_pyusb():
    """Try to use PyUSB if available"""
    print("\n" + "=" * 60)
    print("USB DEVICES (via PyUSB)")
    print("=" * 60)

    try:
        import usb.core
        import usb.util

        devices = usb.core.find(find_all=True)
        device_list = list(devices)

        if not device_list:
            print("No devices found via PyUSB")
            return

        for i, dev in enumerate(device_list, 1):
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
            except:
                pass

            print(f"   Bus: {dev.bus}, Address: {dev.address}")

    except ImportError:
        print("PyUSB not installed. Install with: pip3 install pyusb")
        print("Note: PyUSB also requires libusb: brew install libusb")


def find_silicon_labs_device():
    """Find CP2102N devices using pyusb and map to serial port"""
    try:
        import usb.core
        import usb.util
        import os
        import glob
    except ImportError:
        print("PyUSB not installed. Install with: pip3 install pyusb")
        print("Note: PyUSB also requires libusb: brew install libusb")
        return []

    # Silicon Labs CP210x VID is 0x10C4
    # CP2102N PID is 0xEA60
    SILICON_LABS_VID = 0x10C4
    CP2102N_PID = 0xEA60

    devices = []

    # Find all Silicon Labs CP2102N devices using pyusb
    usb_devices = usb.core.find(find_all=True, idVendor=SILICON_LABS_VID, idProduct=CP2102N_PID)

    for dev in usb_devices:
        device_info = {
            'name': 'CP2102N USB to UART Bridge Controller',
            'vendor_id': f"0x{dev.idVendor:04x}",
            'product_id': f"0x{dev.idProduct:04x}",
            'bus': dev.bus,
            'address': dev.address
        }

        # Try to get additional device info
        try:
            if dev.manufacturer:
                device_info['manufacturer'] = dev.manufacturer
            if dev.product:
                device_info['product'] = dev.product
            if dev.serial_number:
                device_info['serial'] = dev.serial_number
        except:
            pass

        # Find the serial port on macOS - look for SLAB (Silicon Labs) device
        try:
            tty_output = run_command("ls /dev/tty.*")
            print(tty_output)
            if tty_output and not tty_output.startswith('Error'):
                ports = tty_output.strip().split('\n')
                for port in ports:
                    if 'SLAB' in port:
                        device_info['port'] = port
                        break
        except Exception as e:
            print(f"Warning: Could not determine serial port: {e}")

        devices.append(device_info)

    # Print device information
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


def main():
    """Main function to run all enumeration methods"""
    print("\n" + "=" * 60)
    print("MAC DEVICE ENUMERATION TOOL")
    print("=" * 60)

    # Try multiple methods
    parse_ioreg_usb()
    list_usb_system_profiler()
    check_pyusb()
    list_thunderbolt_devices()
    list_storage_devices()
    list_network_interfaces()

    print("\n" + "=" * 60)
    print("ENUMERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
    print(find_silicon_labs_device())
