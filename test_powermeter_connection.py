"""Standalone connection test for the Ophir/Newport powermeters over USB.

Does not import powermeter.py or touch the GUI/queue machinery - it only
exercises the OphirLMMeasurement COM object directly (see
LMMeasurement-COM-Object-Manual, sections 3.6.2 "Device Communications" and
3.6.3 "General Information and Diagnostics") to confirm the meters enumerate
on USB and report sensor info. Windows-only (requires pywin32 + StarLab/
PMManager drivers installed).

Usage: python test_powermeter_connection.py
"""

try:
    import win32com.client
    import win32com.client.gencache
    import pythoncom
except ImportError:
    raise SystemExit(
        "win32 modules are not available on this platform. "
        "This test must be run on Windows with pywin32 installed."
    )


def decode_error(com, err):
    """Best-effort translation of a COM error into the manual's error string."""
    hresult = getattr(err, "hresult", None)
    if hresult is None and err.args and isinstance(err.args[0], int):
        hresult = err.args[0]
    if hresult is None:
        return str(err)
    try:
        return f"0x{hresult & 0xFFFFFFFF:08X}: {com.GetErrorFromCode(hresult)}"
    except Exception:
        return f"0x{hresult & 0xFFFFFFFF:08X} ({err})"


def main():
    print("Initializing COM...")
    pythoncom.CoInitialize()

    print("Connecting to OphirLMMeasurement.CoLMMeasurement...")
    # EnsureDispatch (not plain Dispatch) forces win32com to build/load the
    # makepy type-library wrapper, giving an *early-bound* object. The Ophir
    # methods (StopAllStreams, CloseAll, ScanUSB, ...) are only reachable via
    # the typelib interface; a plain Dispatch falls back to late binding when
    # no gen_py cache exists and every one of those calls raises AttributeError.
    com = win32com.client.gencache.EnsureDispatch(
        "OphirLMMeasurement.CoLMMeasurement"
    )

    try:
        com.StopAllStreams()
        com.CloseAll()

        print("Scanning USB for devices...")
        serial_numbers = com.ScanUSB()
        if not serial_numbers:
            print("No powermeters found on USB.")
            return

        print(f"Found {len(serial_numbers)} device(s): {list(serial_numbers)}")

        for serial in serial_numbers:
            print(f"\n--- Device {serial} ---")
            try:
                handle = com.OpenUSBDevice(serial)
            except Exception as err:
                print(f"  Failed to open device: {decode_error(com, err)}")
                continue

            try:
                name, rom_version, device_serial = com.GetDeviceInfo(handle)
                print(f"  Name: {name}")
                print(f"  ROM version: {rom_version}")
                print(f"  Serial number: {device_serial}")
            except Exception as err:
                print(f"  GetDeviceInfo failed: {decode_error(com, err)}")

            for channel in (0, 1):
                try:
                    exists = com.IsSensorExists(handle, channel)
                except Exception as err:
                    print(f"  Channel {channel}: IsSensorExists failed: {decode_error(com, err)}")
                    continue

                if not exists:
                    print(f"  Channel {channel}: no sensor attached")
                    continue

                try:
                    sensor_serial, sensor_type, sensor_name = com.GetSensorInfo(handle, channel)
                    print(
                        f"  Channel {channel}: sensor OK - "
                        f"serial={sensor_serial}, type={sensor_type}, name={sensor_name}"
                    )
                except Exception as err:
                    print(f"  Channel {channel}: GetSensorInfo failed: {decode_error(com, err)}")

            try:
                com.Close(handle)
            except Exception as err:
                print(f"  Failed to close device: {decode_error(com, err)}")

    finally:
        try:
            com.CloseAll()
        except Exception as err:
            print(f"Cleanup CloseAll failed: {decode_error(com, err)}")
        pythoncom.CoUninitialize()
        print("\nDone.")


if __name__ == "__main__":
    main()
