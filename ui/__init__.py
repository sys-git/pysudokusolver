
from PyQt4 import QtGui, uic
from ui.display import display
import os
import sys

def runPySu(args=sys.argv[1:]):
    app = QtGui.QApplication(sys.argv)
    resourcesPath = os.path.join(os.path.dirname(__file__), "resources")
    path = os.path.join(resourcesPath, display.RESOURCE_NAME)
    inst = display(resourcesPath, 3)
    uic.loadUi(path, baseinstance = inst)
    inst.show()
    app.exec_() # Run the UI

if __name__ == '__main__':
    runPySu(sys.argv[1:])
