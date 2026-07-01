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