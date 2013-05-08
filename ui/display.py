'''
Created on Apr 22, 2013

@author: francis.horsman:gmail.com
'''

from PyQt4 import QtGui, QtCore, uic
from newer.models.cell import cell
from newer.models.element import element
from newer.models.grid import grid
from newer.models.iModelNotifications import iModelNotifications
from newer.models.state import state
from newer.solver.Solved import Solved
from newer.solver.Solver import Solver
from newer.solver.Solving import Solving
import math
import os
import traceback

def setCommonWidgetColour(widget, solver):
    if solver.solved==True:
        widget.setStyleSheet("QWidget { background-color: green; }")
    elif solver.unsolvable==True:
        widget.setStyleSheet("QWidget { background-color: orange; }")
    else:
        widget.setStyleSheet("QWidget { background-color: red; }")

class display_element(QtGui.QWidget):
    RESOURCE_NAME = "element.ui"
    def __init__(self, parent, resourcesPath, size, row, col):
        super(display_element, self).__init__(parent)
        self._resourcesPath = resourcesPath
        self._row = row
        self._size = size
        self._maxSize = int(math.pow(self._size, 2))
        self._col = col
        self._parent = parent
    def show(self):
        super(display_element, self).show()
        self._build()
    def _build(self):
        self.clear()
    def clear(self):
        for count in xrange(int(self._maxSize)):
            possible = getattr(self, "possible_%(C)s"%{"C":count})
            possible.setText("")
            possible.setEnabled(False)
        self.value.setText("")
    def populate(self, solver):
        hasValue = solver.hasValue()
        if hasValue:
            value = solver.getValue()
            self.value.setText(str(value))
            self.value.setEnabled(True)
        setCommonWidgetColour(self, solver)
        if not hasValue:
            for unknown in list(solver.getPossibles()):
                possible = getattr(self, "possible_%(C)s"%{"C":unknown})
                possible.setText(str(unknown))
                possible.setEnabled(True)

class display_cell(QtGui.QWidget):
    RESOURCE_NAME = "cell.ui"
    def __init__(self, parent, resourcesPath, size, row, col):
        super(display_cell, self).__init__(parent)
        self._resourcesPath = resourcesPath
        self._row = row
        self._col = col
        self._size = size
        self._parent = parent
    def show(self):
        super(display_cell, self).show()
        self.cell.setTitle("cell ( %s, %s )"%(self._row, self._col))
        self._build()
    def _build(self):
        self._elements = []
        for row in xrange(self._size):
            _row = []
            self._elements.append(_row)
            for col in xrange(self._size):
                _row.append([])
                x = 10+((0+72)*col)
                y = 20+((0+72)*row)
                self._loadElement(row, col, x, y)
    def _loadElement(self, row, col, x, y):
        el = display_element(self, self._resourcesPath, self._size, row, col)
        path = os.path.join(self._resourcesPath, display_element.RESOURCE_NAME)
        uic.loadUi(path, baseinstance=el)
        self._elements[row][col] = el
        el.move(x, y)
        el.show()
    def populate(self, solver):
        setCommonWidgetColour(self, solver)
        [element.populate(solver.getElementAt(row, col)) for row, col, element in self._iterElements()]
    def clear(self):
        [element.clear() for _row, _col, element in self._iterElements()]
    def _iterElements(self):
        for row in xrange(self._size):
            for col in xrange(self._size):
                yield row, col, self._elements[row][col]
    def getElement(self, row, col):
        return self._elements[row][col]

class customWindow(QtGui.QFrame):
    RESOURCE_NAME = "custom_window.ui"
    def __init__(self, realParent, parent, resourcesPath):
        super(customWindow, self).__init__(parent)
        self._parent = realParent
        self._resourcesPath = resourcesPath
    def show(self):
        super(customWindow, self).show()
        self.connect(self._parent, QtCore.SIGNAL('customEvent(PyQt_PyObject)'), self._onCustomEvent, QtCore.Qt.QueuedConnection)
#         print "yes!"
    def _onCustomEvent(self, args):
#         print "yehaw!"
        self._addCustomEvent(args)
    def _addCustomEvent(self, args):
        _who = args[0]
        _event = args[1]
        _details = args[2]
        row = 0
        self.tableEvents.insertRow(0)
        self.tableEvents.setItem(row, 0, QtGui.QTableWidgetItem("%s"%_details["strategy"]));
        self.tableEvents.setItem(row, 1, QtGui.QTableWidgetItem("%s"%_details["difficulty"]));
        self.tableEvents.setItem(row, 3, QtGui.QTableWidgetItem("%s"%_details["timeStart"]));
        try:
            self.tableEvents.setItem(row, 2, QtGui.QTableWidgetItem("%s"%_details["yield"]));
            self.tableEvents.setItem(row, 4, QtGui.QTableWidgetItem("%s"%_details["timeEnd"]));
            self.tableEvents.setItem(row, 5, QtGui.QTableWidgetItem("%d"%(_details["timeEnd"]-_details["timeStart"])));
        except Exception, _e:
            pass

class display(QtGui.QMainWindow):
    RESOURCE_NAME = "mainwindow.ui"
    def __init__(self, resourcesPath, size):
        super(display, self).__init__()
        self._size = size
        self._maxSize = int(math.pow(size, 2))
        self._resourcesPath = resourcesPath
        self._solver = None
        self._filename = "game.pysu"
        self._build()
    def show(self):
        super(display, self).show()
        self.connect(self, QtCore.SIGNAL('Initialized()'), self._onMainWindowReady, QtCore.Qt.QueuedConnection)
        self.connect(self.buttonSolve, QtCore.SIGNAL('clicked()'), self._onActionSolve, QtCore.Qt.QueuedConnection)
        self.connect(self.actionPopulateSolvable1, QtCore.SIGNAL('triggered()'), self._onActionPopulateSolvable1, QtCore.Qt.QueuedConnection)
        self.connect(self.actionPopulateUnsolvable1, QtCore.SIGNAL('triggered()'), self._onActionPopulateUnsolvable1, QtCore.Qt.QueuedConnection)
        self.connect(self.actionPopulateXWing1, QtCore.SIGNAL('triggered()'), self._onActionPopulateXWing1, QtCore.Qt.QueuedConnection)
        self.connect(self.actionLoad, QtCore.SIGNAL('triggered()'), self._onActionLoad, QtCore.Qt.QueuedConnection)
        self.connect(self.actionSave, QtCore.SIGNAL('triggered()'), self._onActionSave, QtCore.Qt.QueuedConnection)
        self.connect(self, QtCore.SIGNAL('aResult(PyQt_PyObject)'), self._onAResult, QtCore.Qt.QueuedConnection)
        self.connect(self, QtCore.SIGNAL('rePopulate(PyQt_PyObject)'), self._onRepopulate, QtCore.Qt.QueuedConnection)
        self.buttonSolve.setEnabled(False)
        self._loadCustomWindow()
        iconPath = os.path.join(self._resourcesPath, "icons", "su.jpg")
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.emit(QtCore.SIGNAL('Initialized()'))
    def _loadCustomWindow(self):
        cw = customWindow(self, self.frameCustom, self._resourcesPath)
        path = os.path.join(self._resourcesPath, customWindow.RESOURCE_NAME)
        uic.loadUi(path, cw)
        cw.show()
    def _build(self):
        self._cells = []
        for row in xrange(self._size):
            _row = []
            self._cells.append(_row)
            for col in xrange(self._size):
                _row.append([])
                x = 20+((10+231)*col)
                y = 20+((30+231)*row)
                self._loadCell(row, col, x, y)
    def _loadCell(self, row, col, x, y):
        cell = display_cell(self, self._resourcesPath, self._size, row, col)
        path = os.path.join(self._resourcesPath, display_cell.RESOURCE_NAME)
        uic.loadUi(path, baseinstance=cell)
        self._cells[row][col] = cell
        cell.move(x, y)
        cell.show()
    def _modelListener(self, who, event, args=None):
        if event==iModelNotifications.CUSTOM():
            self.emit(QtCore.SIGNAL('customEvent(PyQt_PyObject)'), (who, event, args))
        if who==grid.NAME:
            self.emit(QtCore.SIGNAL('rePopulate(PyQt_PyObject)'), event)
        else:
            self.emit(QtCore.SIGNAL('aResult(PyQt_PyObject)'), args)
    def _onCustomEvent(self, args):
        self._addCustomEvent(args)
    def _onActionSolve(self):
        if self._solver!=None:
            try:
                self._solver.solve()
                self.buttonSolve.setEnabled(False)
            except Solved, _e:
                print "already solved!"
                self._setSolved()
            except Solving, _e:
                print "already solving!"
                self._setSolving()
            except Exception, _e:
                raise
    def _onActionPopulateSolvable1(self):
        self._abortSolver()
        self._solver = None
        newData = [[None, None, None,   1, None, 5,         None, 6, 8],
                   [None, None, None,   None, None, None,   7, None, 1], 
                   [0, None, 1,         None, None, None,   None, 3, None], 
                   [None, None, 7,      None, 2, 6,         None, None, None],
                   [5, None, None,      None, None, None,   None, None, 3],
                   [None, None, None,   8, 7, None,         4, None, None],
                   [None, 3, None,      None, None, None,   8, None, 5],
                   [1, None, 5,         None, None, None,   None, None, None],
                   [7, 0, None,         4, None, 1,         None, None, None]]
        self._onActionLoad(newData)
        print self._solver.model.prettyprint()
        self.buttonSolve.setEnabled(True)
        self._rePopulate()
    def _onActionPopulateUnsolvable1(self):
        self._abortSolver()
        self._solver = None
        newData  = [[None, None, 6,     None, None, None,   None, None, 4],
                   [None, None, None,   8, 6, None,         7, 3, None], 
                   [None, 4, None,      3, 5, None,         None, None, 2], 
                   [1, 7, None,         4, None, None,      6, None, None],
                   [None, 0, None,      None, None, None,   None, 8, None],
                   [None, None, 8,      None, None, 6,      None,  1, 7],
                   [2, None, None,      None, 8, 1,         None, 4, None],
                   [None, 6, 7,         None, 4, 3,         None, None, None],
                   [8, None, None,      None, None, None,   3, None, None]]
        self._onActionLoad(newData)
        print self._solver.model.prettyprint()
        self.buttonSolve.setEnabled(True)
        self._rePopulate()
    def _onActionPopulateXWing1(self):
        self._abortSolver()
        self._solver = None
        newData  = [[1, None, None,     None, None, None,   5, 6, 0],
                   [4, 0, 2,            None, 5, 6,         1, None, 8], 
                   [None, 5, 6,         1, None, 0,         2, 4, None], 
                   [None, None, 0,      6, 4, None,         8, None, 1],
                   [None, 6, 4,         None, 1, None,      None, None, None],
                   [2, 1, 8,            None, 3, 5,         6,  None, 4],
                   [None, 4, None,      5, None, None,      None, 1, 6],
                   [0, None, 5,         None, 6, 1,         4, None, 2],
                   [6, 2, 1,            None, None, None,   3, None, 5]]
        self._onActionLoad(newData)
        print self._solver.model.prettyprint()
        self.buttonSolve.setEnabled(True)
        self._rePopulate()
    def iterCells(self):
        for row in xrange(self._size):
            for col in xrange(self._size):
                yield row, col, self._cells[row][col]
    def _setSolve(self):
        self.buttonSolve.setEnabled(True)
        self.buttonSolve.setText("Solve")
    def _setSolved(self):
        self.buttonSolve.setText("Solved")
        self.buttonSolve.setEnabled(False)
        self._solver.model.regenerateKnowns()
        self._populateKnowns()
    def _setSolving(self):
        self.buttonSolve.setText("Solving")
        self.buttonSolve.setEnabled(False)
    def _populate(self):
        if self._solver.model.solved==True:
            self._setSolved()
        self._solver.model.regenerateKnowns()
        self._populateKnowns()
        [cell.populate(self._solver.model.getCellAt(row, col)) for row, col, cell in self.iterCells()]
    def _clearCells(self):
        self._clearKnowns()
        [cell.clear() for _row, _col, cell in self.iterCells()]
    def _populateKnowns(self):
        knowns = self._solver.model.knowns()
        for i in knowns:
            button = getattr(self, "found_%s"%i)
            button.setEnabled(True)
            button.setText(str(i))
            button.setStyleSheet("QWidget { background-color: green; }")
    def _clearKnowns(self):
        for i in xrange(self._maxSize):
            button = getattr(self, "found_%s"%i)
            button.setEnabled(False)
            button.setText(str(i))
            button.setStyleSheet("QWidget { background-color: red; }")
    def _onActionLoad(self, data=None):
        self._abortSolver()
        self._solver = None
        solver = Solver(grid(self._size))
        if data==None:
            try:
                with open(self._filename, "r") as g:
                    game = g.read()
                    print "Loaded game!"
                    solver.deserialize(game)
                    print solver.model.prettyprint()
            except Exception, _e:
                print "Failed to load game:\n%s"%traceback.format_exc()
        else:
            solver.data(data)
        solver.addListener(self._modelListener)
        self._solver = solver
        try:
            self._solver.model.checkValidation()
        except Solved, _e:
            #    All solved so make everything green!
            self._setSolved()
            return
        self._solver.model._state = state.UNSOLVED
        self._setSolve()
        self._rePopulate()
    def _onAResult(self, uref):
        if uref.name==element.NAME:
            r = uref.offsetRow+uref.row
            c = uref.offsetCol+uref.col
            row = divmod((r),self._size)
            col = divmod((c),self._size)
            modelCell = self._solver.model.getCellAt(row[0], col[0])
            model = modelCell.getElementAt(row[1], col[1])
            cell_ = self._cells[row[0]][col[0]]
            elementUI = cell_.getElement(row[1], col[1])
            elementUI.populate(model)
        elif uref.name==cell.NAME:
            cellUI = self._cells[uref.row][uref.col]
            model = self._solver.model.getCellAt(uref.row, uref.col)
            cellUI.populate(model)
    def _onRepopulate(self, event):
        if event==iModelNotifications.UNSOLVABLE():
            self.buttonSolve.setText("Unsolvable")
        self._rePopulate()
    def _rePopulate(self, args=None):
        self._clearCells()
        self._populate()
    def _onMainWindowReady(self):
        pass
    def closeEvent(self, event):
        self._abortSolver()
        self._onActionSave()
        event.accept()
    def _onActionSave(self):
        if self._solver!=None:
            game = self._solver.serialize()
            with open(self._filename, "w") as g:
                g.write(game)
                print "Saved game!"
    def _abortSolver(self):
        try:
            self._solver.abort()
        except Exception, _e:
            pass
