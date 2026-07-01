PS C:\Users\OSA\dev\tissueSquisherDataAnalysis> uv run main.py
agiltronController.py - start called
Platform detected: Windows
Platform detected: Windows
Searching COM ports for Silicon Labs device...
No Silicon Labs device found on COM ports.
Serial connection error: could not open port 'COM3': FileNotFoundError(2, 'The system cannot find the file specified.', None, 2)
[Error] Failed to open discovered port COM3
Stage controller failed to connect
Polarimeter Connection Error
no powermeters connected. Note: you must be on windows.
Powermeters connected successfully
Exception in thread Thread-3 (start):
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\powermeter.py", line 84, in start
    target=self.__runDevice1, args=[self.deviceList[0]]
                                    ^^^^^^^^^^^^^^^
AttributeError: 'Powermeter' object has no attribute 'deviceList'
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tkinter\__init__.py", line 1968, in __call__
    return self.func(*args)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tkinter\__init__.py", line 862, in callit
    func(*args)
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\gui.py", line 944, in updatePlotsFromData
    self.power1Text.set(str(self.powermeter.device1Data))
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Powermeter' object has no attribute 'device1Data'
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tkinter\__init__.py", line 1968, in __call__
    return self.func(*args)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\gui.py", line 214, in stop
    self.powermeter.stop()
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\powermeter.py", line 173, in stop
    self.run.clear()
    ^^^^^^^^
AttributeError: 'Powermeter' object has no attribute 'run'
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tkinter\__init__.py", line 1968, in __call__
    return self.func(*args)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\gui.py", line 214, in stop
    self.powermeter.stop()
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\powermeter.py", line 173, in stop
    self.run.clear()
    ^^^^^^^^
AttributeError: 'Powermeter' object has no attribute 'run'
Exception in Tkinter callback
Traceback (most recent call last):
  File "C:\Users\OSA\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\tkinter\__init__.py", line 1968, in __call__
    return self.func(*args)
           ^^^^^^^^^^^^^^^^
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\gui.py", line 214, in stop
    self.powermeter.stop()
  File "C:\Users\OSA\dev\tissueSquisherDataAnalysis\powermeter.py", line 173, in stop
    self.run.clear()
    ^^^^^^^^
AttributeError: 'Powermeter' object has no attribute 'run'



no powermeters connected (com_error: (-2147023782, 'A dynamic link library (DLL) initialization routine failed.', None, None)). Note: you must be on windows with two Ophir powermeters attached.
Powermeter Connection Error ((-2147023782, 'A dynamic link library (DLL) initialization routine failed.', None, None)). You need two powermeters connected at all times.