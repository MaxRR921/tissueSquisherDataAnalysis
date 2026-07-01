PS C:\Users\OSA\dev\tissueSquisherDataAnalysis> python .\test_powermeter_connection.py
Initializing COM...
Connecting to OphirLMMeasurement.CoLMMeasurement...
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\win32com\client\gencache.py", line 643, in EnsureDispatch
    ti = disp._oleobj_.GetTypeInfo()
pywintypes.com_error: (-2147319779, 'Library not registered.', None, None)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\test_powermeter_connection.py", line 114, in <module>
    main()
    ~~~~^^
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\test_powermeter_connection.py", line 47, in main
    com = win32com.client.gencache.EnsureDispatch(
        "OphirLMMeasurement.CoLMMeasurement"
    )
  File "C:\Users\OSA\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\win32com\client\gencache.py", line 655, in EnsureDispatch
    raise TypeError(
        "This COM object can not automate the makepy process - please run makepy manually for this object"
    )
TypeError: This COM object can not automate the makepy process - please run makepy manually for this object



PS C:\Users\OSA\dev\tissueSquisherDataAnalysis> python main.py
agiltronController.py - start called
Platform detected: Windows
Platform detected: Windows
Searching COM ports for Silicon Labs device...
No Silicon Labs device found on COM ports.
Serial connection error: could not open port 'COM3': FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)
[Error] Failed to open discovered port COM3
Stage controller failed to connect
Polarimeter Connection Error
no powermeters connected (com_error: (-2147221005, 'Invalid class string', None, None)). Note: you must be on windows with two Ophir powermeters attached.
Powermeter Connection Error ((-2147221005, 'Invalid class string', None, None)). You need two powermeters connected at all times.



