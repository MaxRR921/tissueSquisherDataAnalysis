import dataAnalysisVmaster as analysis
import Gui as gui
import controller

ser = controller.initialize()
gui.run(ser)
controller.onQuit(ser)
#controller.initialize()