#research #note #school  
# Fiber Optic Stress Sensor Data Collection and Analysis Software

## Goals 
The Fiber Optic Stress Sensor, originally developed by Dr. Harrison, uses fiber optic cable that guides linearly polarized light from a lazer into a section of fiber that lies under a sample. The sample is stressed using a micrometer and presshead, changing the polarization state of the light, and then enters a polarimeter sensing element. We have adjusted the setup to use a dual-powermeter setup with a splitter that splits the light exiting the stressed section into two orthogonal components. We then measure the normalized difference between the powers measured using the two powermeters. 
  
This software interfaces with four devices: the two powermeters, the polarimeter, and the micrometer. It provides a GUI interface to collect data from the the sensors and control the micrometer to compress and decompress the sample. It provides an GUI to add and execute a sequence of moves to the micrometer, and easily synchronizes data collection from the sensing elements with this sequence of moves. Additionally, it displays plots in real time using a seperate PyQTGraph process. The sensors and micrometer write data to buffers initialized in the python code, which are written to CSVs and sent to the PyQTGraph process. This allows the user to see quick plots in realtime which significantly increases the efficiency of data collection. Since the devices also store data in buffers that write to CSV's after the sequence of moves is executed, the user can perform further analysis after viewing the realtime plots. 

## How To Run  
**Required Devices:** Two Newport 845-PE-RS Virtual Optical Powermeters, One Newport TRB12CC linear actuator and CONEX-CC controller
     
**Recommended Devices (if you want to actually build the stress sensor and replicate our tests):** Thorlabs PAX1000 series polarimeter, PM fiber optic cable (jacketed and bare), 1550 Nm 50 mw laser, linear stage, presshead    
  
## Download Source Code
**Required Dependencies:** numpy, tkinter, time, threading, tkthemes, csv, multiprocessing, sys, PyQt5, scipy, ctypes, queue, serial, win32com.client, pythoncom


## Software Structure 
main.py instantiates a Gui object and calls gui.run. 

the **gui** class instantiates all device objects: powermeters, micrometer (controller.py) and polarimeter. Each one of these devices is initialized on a new thread.  
  
The **powermeters** start taking data immediately, but when the program isn't in the collection state (e.g. when the micrometer moves are   inputted and are in the process of executing), they display the newest reading on the screen then simply throw it away. You must have the necessary windows-exclusive drivers installed in order to use the powermeters. See important links.
  
The **polarimeter** is initialized when the program starts, and only starts sending the program data when the micrometer movement is executed. Additionally, after every sequence of micrometer movements, the polarimeter is reinitialized to avoid bugs. user MUST have the required polarimeter drivers installed see important links. The polarimeter does not display data in real time because of the extensive mathematical processing that needs to be executed to convert the data from the stokes parameter to delta polarizaiton form. 
  
The **micrometer** is sent commands via the serial port and the program only recieves data while it is in motion. 

The gui is simple, and includes the ability to add moves. Each move has a target position, a velocity, and a front and back wait where the user can decide how much the micrometer will wait before or after it executes the move. you can add any number of moves, and either execute them individually or save and execute them all in order any number of times.  
  
Additionally, the software includes the ability to display real time plots, which currently consist of a micrometer position vs. time plot, a powermeter1 vs. time plot, a powermeter2 vs. time plot, a normalized power difference vs. time plot and a delta pol vs. time plot, which does not update in real time.   
  
As data is taken from each sensor, it is added to queues that are dispatched from the producer thread to the consumer PyQtGraph process. the PyQtGraph process dequeues data from the queues into arrays (slow, I know, but the PyQtGraphs can only plot array to my knowledge), which are then plotted. Each device thread also keeps a seperate queue from the one that is read in the PyQtGraph process and dumps it all into a csv so we can perform later analysis. 


![Software main screen](bjasldfjas.png)