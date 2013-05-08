'''
Created on Mar 29, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.URef import URef
from newer.models.iModelNotifications import iModelNotifications
from newer.models.link import link
from newer.models.state import state
from sets import Set
import copy
import math
import traceback

class helper(object):
    def __init__(self, row, col, size):
        self._row = row
        self._col = col
        self._size = size
        self._maxSize = int(math.pow(size, 2))
        self._links = {link.HORIZONTAL:[], link.VERTICAL:[]}
        self._listeners = {"parent":[], "other":[]}
        self._dirty = False
        self._state = state.UNSOLVED
        self._fixing = False
        self._notifying = False
    def setState(self, newState):
        if self._state!=newState:
            self._state = newState
            event = iModelNotifications.UPDATE()
            if self._state==state.UNSOLVABLE:
                event = iModelNotifications.UNSOLVABLE()
            elif self._state==state.SOLVED:
                event = iModelNotifications.SOLVED()
            self._notifyListener(self.NAME, event, self.uRef)
            self._notifyParentListener(self.NAME, event, self.uRef)
    def getIsUnsolvable(self):
        return self._state==state.UNSOLVABLE
    def setIsUnsolvable(self, bUnsolvable):
        if bUnsolvable==True:
            self.setState(state.UNSOLVABLE)
    def getIsSolved(self):
        return self._state==state.SOLVED
    def setIsSolved(self, bState):
        if bState==True:
            s = state.SOLVED
        else:
            s = state.UNSOLVED
        if self._state!=s:
            self._state = s
            if s==state.SOLVED:
                self._notifyListener(self.NAME, iModelNotifications.SOLVED(), self.uRef)
            else:
                self._notifyListener(self.NAME, iModelNotifications.UPDATE(), self.uRef)
    solved = property(getIsSolved, setIsSolved)
    unsolvable = property(getIsUnsolvable, setIsUnsolvable)
    def isValid(self):
        return self._valid
    def getRow(self):
        return self._row
    def getCol(self):
        return self._col
    def _getUref(self):
        #    Override as required.
        return URef(self.NAME, self._size, self.row, self.col)
    def getUref(self):
        return self._getUref()
    row = property(getRow)
    col = property(getCol)
    uRef = property(getUref)
    def xvalues(self):
        return xrange(self._maxSize)
    def values(self):
        return range(self._maxSize)
    def link(self, direction, items):
        self._links[direction] = copy.copy(items)
        self._links[direction].remove(self)
        for link in self._links[direction]:
            link.addListener(self)
    def addListener(self, listener):
        self.removeListener(listener)
        self._listeners["other"].append(listener)
    def removeListener(self, listener):
        try:
            self._listeners["other"].remove(listener)
            return True
        except Exception, _e:
            pass
    def addParentListener(self, listener):
        self.removeParentListener(listener)
        self._listeners["parent"].append(listener)
    def removeParentListener(self, listener):
        try:
            self._listeners["parent"].remove(listener)
            return True
        except Exception, _e:
            pass
    def _notifyParentListener(self, who, event=None, args=None):
        return self.__notifyListener(self._listeners["parent"], who, event, args)
    def _notifyListener(self, who, event=None, args=None):
        return self.__notifyListener(self._listeners["other"], who, event, args)
    def __notifyListener(self, what, who, event=None, args=None):
        if event!=iModelNotifications.CUSTOM():
            self._dirty = True
        for listener in what:
            try:
                listener.notification(who, event, args)
            except Exception, _e:
                traceback.print_exc()
                raise
    def notification(self, who, event=None, args=None):
        self._dirty = True
    def _getIsDirty(self):
        return self._dirty==True
    isDirty = property(_getIsDirty)
    def notDirty(self, enabler=True):
        self._dirty = not enabler
    @staticmethod
    def createItems(cls, size):
        items = []
        for row in xrange(size):
            for col in xrange(size):
                item = cls(row, col, size)
                assert item.row==row
                assert item.col==col
                items.append(item)
        return items
    @staticmethod
    def getItem(items, size, row=0, col=0):
        index = ((size*row)+col)
        item = items[index]
        assert item.row==row
        assert item.col==col
        return item
    @staticmethod
    def getItemRow(items, size, row):
        result = []
        for col in xrange(size):
            result.append(helper.getItem(items, size, row, col))
        return result
    @staticmethod
    def getItemCol(items, size, col):
        result = []
        for row in xrange(size):
            result.append(helper.getItem(items, size, row, col))
        return result
    @staticmethod
    def getItemRows(items, size):
        for row in xrange(size):
            yield helper.getItemRow(items, size, row)
    @staticmethod
    def getItemCols(items, size):
        for col in xrange(size):
            yield helper.getItemCol(items, size, col)
    @staticmethod
    def linkItems(items, size):
        #    Now link items horizontally:
        for row in xrange(size):
            cols = []
            for col in xrange(size):
                cols.append(helper.getItem(items, size, row, col))
            for col in cols:
                col.link(link.HORIZONTAL, cols)
        #    Now link items vertically:
        cols__ = {}
        for index, col in enumerate(xrange(size)):
            cols_ = []
            for row in xrange(size):
                cols_.append(helper.getItem(items, size, row, col))
            cols__[index] = cols_
        for index, col in cols__.items():
            for c in col:
                c.link(link.VERTICAL, col)
    def fix(self, knowns=[]):
        if self.solved:
            return
        if self._fixing:
            return
        self._fixing = True
        try:
            wasDirty = self.isDirty
            self._dirty = True
            newlyDirty = False
            while (self._dirty==True) and (self.solved==False):
                self._dirty = False
                isSolved = True
                for helper in self.helpers:
                    knowns_ = self.knowns().union(Set(knowns))
                    helper.fix(knowns_)
                    isSolved &= helper.solved
                if isSolved==True:
                    self.solved = True
                newlyDirty |= self._dirty
            self._dirty = (wasDirty or newlyDirty)
        finally:
            self._fixing = False
    def unknowns(self):
        return Set(self.xvalues())-self.knowns()

if __name__ == '__main__':
    pass
