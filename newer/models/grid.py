'''
Created on Mar 29, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.URef import URef
from newer.models.cell import cell
from newer.models.element import element
from newer.models.helper import helper
from newer.models.iModelNotifications import iModelNotifications
from newer.models.state import state
from newer.solver.Solved import Solved
from newer.solver.Solving import Solving
from newer.solver.SudokuModelVerifier import SudokuModelVerifier
from sets import Set
import cPickle

class grid(helper):
    NAME = "grid"
    def __init__(self, size, row=-1, col=-1, values=[]):
        super(grid, self).__init__(row, col, size)
        self._cells = self._createCells(self._size)
        helper.linkItems(self._cells, self._size)
        self._knowns = []   # Optimisation.
    def _createCells(self, size):
        cells = helper.createItems(cell, size)
        for c in cells:
            c.addParentListener(self)
        return cells
    def getCellAt(self, row=0, col=0):
        return helper.getItem(self._cells, self._size, row, col)
    def __str__(self):
        s = ["Grid:"]
        s.append("%(F)s x %(F)s"%{"F":self._maxSize})
        if self._state==state.SOLVED:
            s.append("Completed!")
        elif self._state==state.UNSOLVABLE:
            s.append("Unsolvable!")
        elif self._state==state.UNSOLVED:
            s.append("Unsolved.")
        s.append("\n")
        s.append(self._printCells())
        return " ".join(s)
    def prettyprint(self):
        s = ["--------------------------------------------------------"]
        for row in self.rows:
            for index in xrange(self._size):
                ss = []
                for cell in row:
                    sss = []
                    cellRow = cell.getRow(index)
                    for element in cellRow:
                        sss.append("%(V)04s"%{"V":element.getValue()})
                    ss.append(", ".join(sss))
                s.append("[ "+"| ".join(ss)+" ]")
            s.append("--------------------------------------------------------")
        s1 = ["--------------------------------------------------------"]
        for row in self.rows:
            for index in xrange(self._size):
                ss = []
                for cell in row:
                    sss = []
                    cellRow = cell.getRow(index)
                    for element in cellRow:
                        poss = element.getPossibles()
                        if len(poss)==0:
                            poss = "[None]"
                        else:
                            poss = "%(V)s"%{"V":list(poss)}
                        sss.append(poss)
                    ss.append(", ".join(sss))
                s1.append("[ "+"| ".join(ss)+" ]")
            s1.append("--------------------------------------------------------")
        for index in xrange(len(s)):
            s[index] = s[index] + "    " + s1[index]
        return "\n".join(s)
    def _printCells(self):
        s = ["[\n"]
        for row in self.rows:
            for cell in row:
                s.append(str(cell))
            s.append("\n")
        return " ".join(s)+" ]"
    def getCells(self):
        for cell in self._cells:
            yield cell
    def getElementRows(self):
        for cells in self.rows:
            for index in xrange(self._size):
                row = []
                for cell in cells:
                    row.extend(cell.getRow(index))
                yield row
    def getElementCols(self):
        for cells in self.cols:
            for index in xrange(self._size):
                col = []
                for cell in cells:
                    col.extend(cell.getCol(index))
                yield col
    elementRows = property(getElementRows)
    elementCols = property(getElementCols)
    def getRow(self, row):
        return helper.getItemRow(self._cells, self._size, row)
    def getCol(self, col):
        return helper.getItemCol(self._cells, self._size, col)
    def getRows(self):
        return helper.getItemRows(self._cells, self._size)
    def getCols(self):
        return helper.getItemCols(self._cells, self._size)
    cells = property(getCells)
    rows = property(getRows)
    cols = property(getCols)
    def update(self, items):
        if not isinstance(items, list):
            items = [items]
        oldDirty = self._dirty
        self._dirty = False
        for item in items:
            if isinstance(item, grid):
                self._updateFromGrid(item)
            elif isinstance(item, cell):
                self._updateFromCell(item)
            elif isinstance(item, element):
                self._updateFromElement(item)
            elif isinstance(item, URef):
                self._updateFromUref(item)
        if self.isDirty==True:
            self.fix()
        self._dirty = (oldDirty or self.isDirty)
    def _updateFromUref(self, uref):
        if uref.name==element.NAME:
            cell_, eRow, eCol = self._findCellForElement(uref.row+uref.offsetRow, uref.col+uref.offsetCol)
            el = cell_.getElementAt(eRow, eCol)
            update = element.deserialize(cPickle.loads(uref.data))
            el.update(update)
        elif uref.name==cell.NAME:
            cell_ = self.getCellAt(uref.row, uref.col)
            update = cell_.deserialize(cPickle.loads(uref.data))
            cell_.update(update)
        else:
            raise Exception("Uref update for: '%s'."%uref.name)
    def _findFromUref(self, uref):
        if uref.name==element.NAME:
            cell_, eRow, eCol = self._findCellForElement(uref.row+uref.offsetRow, uref.col+uref.offsetCol)
            el = cell_.getElementAt(eRow, eCol)
            els = el.serialize()
            uref.data = cPickle.dumps(els)
        elif uref.name==cell.NAME:
            cell_ = self.getCellAt(uref.row, uref.col)
            cs = cell_.serialize()
            uref.data = cPickle.dumps(cs)
        else:
            raise Exception("Uref find for: '%s'."%uref.name)
        return uref
    def _findCellForElement(self, elRow, elCol):
        row = divmod((elRow),self._size)
        col = divmod((elCol),self._size)
        cell = self.getCellAt(row[0], col[0])
        return cell, row[1], col[1]
    def findElementsForRow(self, row):
        #    Return all the elements in the row:
        row = [self._findElement(row, col) for col in xrange(self._maxSize)]
        return row
    def findElementsForCol(self, col):
        #    Return all the elements in the col:
        col = [self._findElement(row, col) for row in xrange(self._maxSize)]
        return col
    def findElement(self, elRow, elCol):
        return self._findElement(elRow, elCol)
    def _findElement(self, elRow, elCol):
        cell, row, col = self._findCellForElement(elRow, elCol)
        return cell.getElementAt(row, col)
    def iterElements(self):
        for row in self._maxSize:
            for col in self._maxSize:
                yield self._findElement(row, col)
    def iterUnknownElements(self):
        for row in self._maxSize:
            for col in self._maxSize:
                element = self._findElement(row, col)
                if not element.hasValue():
                    yield element
    def _updateFromElement(self, element):
        elRow = element._offsetRow+element.row
        elCol = element._offsetCol+element.col
        cell, eRow, eCol = self._findCellForElement(elRow, elCol)
        el = cell.getElementAt(eRow, eCol)
        el.update(element)
    def _updateFromGrid(self, grid):
        for cell in grid.cells:
            self._updateFromCell(cell)
        self.setState(grid._state)
    def _updateFromCell(self, cell):
        row = cell.row
        col = cell.col
        c = self.getCellAt(row, col)
        c.update(cell)
    def fix(self):
        super(grid, self).fix()
        knowns = []
        for cell in self.cells:
            knowns.extend(list(cell.knowns()))
        k = Set(knowns)
        allKnowns = []
        for i in list(k):
            c = knowns.count(i)
            if c==self._maxSize:
                allKnowns.append(i)
        self.regenerateKnowns()
        if len(self._knowns)==self._maxSize:
            self.solved = True
            self._notifyParentListener(self.NAME, iModelNotifications.SOLVED())
        return self
    def regenerateKnowns(self):
        knowns = []
        for cell in self.cells:
            knowns.extend(list(cell.knowns()))
        k = Set(knowns)
        allKnowns = []
        for i in list(k):
            c = knowns.count(i)
            if c==self._maxSize:
                allKnowns.append(i)
        self._knowns = list(Set(allKnowns))
    def getHelpers(self):
        return self.cells
    helpers = property(getHelpers)
    def notification(self, who, event=None, args=None):
        try:
            if self._notifying==True:
                return
            self._notifying = True
            try:
                super(grid, self).notification(who)
                self._notifyListener(who, event, args)
            finally:
                self._notifying = False
        finally:
            self._notifyParentListener(who, event, args)
    def knowns(self):
        return Set(self._knowns)
    def deserialize(self, stream):
        return grid._deserialize(stream)
    @staticmethod
    def _deserialize(stream):
        params = cPickle.loads(stream)
        g = grid(params["size"])
        g._knowns = params["knowns"]
        g._state = params["state"]
        cells = []
        for cell_ in params["cells"]:
            c = cell.deserialize(cell_)
            cells.append(c)
        g.update(cells)
        g.notDirty()
        return g
    def serialize(self):
        try:
            params = {"state": self._state,
                      "size": self._size,
                      "knowns": self._knowns,
                      "cells": []}
            for cell in self.cells:
                params["cells"].append(cell.serialize())
            return cPickle.dumps(params)
        finally:
            pass
    def clone(self):
        return self.deserialize(self.serialize())
    def checkValidation(self):
        if self.solved==True:
            self._notifyParentListener(self.NAME, iModelNotifications.SOLVED(), self.uRef)
            raise Solved(self)
    def setData(self, data):
        #    Data is raw rows, cols of values.
        for iRow, row in enumerate(data):
            for iCol, col in enumerate(row):
                cell, r, c = self._findCellForElement(iRow, iCol)
                element = cell.getElementAt(r, c)
                element.setValue(col)
        self.fix()
    def getData(self):
        raise ValueError()
    data = property(getData, setData)
    def getCellsForRow(self, cell):
        cells = []
        if cell!=None:
            row = cell.row
            cells = self.getRow(row)
            cells.remove(cell)
        return cells
    def getCellsForCol(self, cell):
        cells = []
        if cell!=None:
            col = cell.col
            cells = self.getCol(col)
            cells.remove(cell)
        return cells
    def customEvent(self, who=None, args=None):
        if who==None:
            who = grid.NAME
        self._notifyParentListener(who, iModelNotifications.CUSTOM(), args)

if __name__ == '__main__':
    g = grid(2)
    print g
    r = g.rows
    el = element(0, 1, 2)
    g.update(el)
    c = cell(1, 1, 2)
    el = c.getElementAt(1, 1)
    el.setValue(2)
    el = c.getElementAt(1, 0)
    el.setValue(1)
    el = c.getElementAt(0, 0)
    el.setValue(0)
    g.update(c)
    g.fix()
    print g
    g.fix()
    print g
    stream = g.serialize()
    grid1 = g.deserialize(stream)
    print grid1
    grid1.fix()
    print grid1
    grid2 = grid1.clone()
    print grid2
    print "done!"
    try:
        SudokuModelVerifier(grid2)()
    except Solving, _e:
        assert True
    else:
        assert False
