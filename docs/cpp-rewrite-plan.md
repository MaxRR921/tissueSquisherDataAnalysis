---
name: cpp-rewrite-plan
description: Plan to rewrite the Python fiber-sensor control system in C++ with Qt
metadata:
  type: project
---

The user is planning to port this project (currently Python: Tkinter main GUI + PyQt5/pyqtgraph plotting in a separate process) to C++.

Decision direction (as of 2026-06-14): target **Qt Widgets** (not QML, not Dear ImGui). Rationale tied to existing architecture:
- Control UI is forms/lists heavy (params, editable Move list) → retained-mode fits.
- Qt collapses the current Tkinter+PyQt two-framework / multiprocessing split into one event loop, deleting the cross-process `plotQueue`.
- Existing worker-thread + `csvQueue`/`plotQueue` + `updatingCsvQueue`/`updatingPlotQueue` device pattern maps 1:1 onto QThread + queued signals/slots.
- **QSerialPort** chosen over libserialport/Asio (comes with Qt; `QSerialPortInfo` replaces `ConnectionFinder` CP2102N VID/PID lookup).

Proposed C++ layout: `agiltronController.py`→`AgiltronController` (QObject, owns QSerialPort; `on_step` callback → `sampleReady` signal); `stageQueue.py` **dissolves** into signals; `move.py`→`Move` struct + `MoveSequencer` worker; `graphingProcess.py`→in-process `LivePlot` widget (QCustomPlot suggested for realtime); powermeter/polarimeter stay Windows-only via `#ifdef _WIN32`. Build via CMake + Qt6 (Widgets/SerialPort/Charts).

Still exploratory — not yet committed/started. The Windows COM powermeter/polarimeter port is the hardest part and is GUI-independent.
