PS C:\Users\OSA\dev\tissueSquisherDataAnalysis> python .\test_powermeter_connection.py
Initializing COM...
Connecting to OphirLMMeasurement.CoLMMeasurement...
Traceback (most recent call last):
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\test_powermeter_connection.py", line 44, in main
    com.StopAllStreams()
    ^^^^^^^^^^^^^^^^^^
  File "C:\Users\OSA\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\win32com\client\dynamic.py", line 631, in __getattr__
    raise AttributeError(f"{self._username_}.{attr}")
AttributeError: OphirLMMeasurement.CoLMMeasurement.StopAllStreams

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\test_powermeter_connection.py", line 103, in <module>
    main()
    ~~~~^^
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\test_powermeter_connection.py", line 97, in main
    com.CloseAll()
    ^^^^^^^^^^^^
  File "C:\Users\OSA\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\win32com\client\dynamic.py", line 631, in __getattr__
    raise AttributeError(f"{self._username_}.{attr}")
AttributeError: OphirLMMeasurement.CoLMMeasurement.CloseAll