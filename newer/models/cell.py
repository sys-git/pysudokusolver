'''
Created on Mar 29, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.LogicError import LogicError
from newer.models.element import element
from newer.models.helper import helper
from sets import Set

class cell(helper):
    NAME = "cell"
    def __init__(self, row, col, size, values=[]):
        super(cell, self).__init__(row, col, size)
        self._elements = self._createElements(self._size, row, col)
        helper.linkItems(self._elements, self._size)
    def _createElements(self, size, row, col):
        elements = helper.createItems(element, size)
        for el in elements:
            el._offsetCol = (size*col)
            el._offsetRow = (size*row)
            el.addParentListener(self)
        return elements
    def getElementAt(self, row=0, col=0):
        return helper.getItem(self._elements, self._size, row, col)
    def __str__(self):
        state = "unsolved"
        if self.solved==True:
            state = "solved"
        s = ["cell[%(R)s, %(C)s] (%(S)s):"%{"R":self._row, "C":self._col, "S":state}]
        s.append("[")
        for index, row in enumerate(self.rows):
            for element in row:
                s.append(str(element))
            if index+1<self._size:
                s.append("|")
        s.append("]")
        return " ".join(s)
    def getElements(self):
        for element in self._elements:
            yield element
    def getRow(self, row):
        return helper.getItemRow(self._elements, self._size, row)
    def getCol(self, col):
        return helper.getItemCol(self._elements, self._size, col)
    def getRows(self):
        return helper.getItemRows(self._elements, self._size)
    def getCols(self):
        return helper.getItemCols(self._elements, self._size)
    elements = property(getElements)
    rows = property(getRows)
    cols = property(getCols)
    def update(self, c):
        if not isinstance(c, cell):
            raise TypeError(c)
        for row in xrange(self._size):
            for col in xrange(self._size):
                elMoi = self.getElementAt(row, col)
                elOther = c.getElementAt(row, col)
                elMoi.update(elOther)
        self.fix()
    def knowns(self):
        knowns = []
        for element in self.elements:
            if element.hasValue():
                value = element.getValue()
                if value in knowns:
                    raise LogicError(value, knowns)
                knowns.append(value)
        knowns.sort()
        return Set(knowns)
    def notification(self, who, event=None, args=None):
        try:
            if self._notifying==True:
                return
            self._notifying = True
            try:
                super(cell, self).notification(who, event, args)
                self.fix()
            finally:
                self._notifying = False
        finally:
            self._notifyParentListener(who, event, args)
    def getHelpers(self):
        return self.elements
    helpers = property(getHelpers)
    def serialize(self):
        params = {"state": self._state,
                  "row": self.row,
                  "col": self.col,
                  "size": self._size,
                  "elements": []}
        for el in self.elements:
            params["elements"].append(el.serialize())
        return params
    @staticmethod
    def deserialize(stream):
        c = cell(stream["row"], stream["col"], stream["size"])
        c._state = stream["state"]
        elements = []
        for el in stream["elements"]:
            elements.append(element.deserialize(el))
        for index, el in enumerate(c.elements):
            e = elements[index]
            el.update(e)
        el.notDirty()
        return c
    def coords(self, knownValue):
        for element in self.elements:
            if element.hasValue():
                if element.getValue()==knownValue:
                    return element.row, element.col
    def unknown(self):
        unknowns = list(self.unknowns())
        if len(unknowns)==1:
            for el in self.elements:
                if not el.hasValue():
                    return (el, unknowns[0])
        return (None, None)
    def uniqueUnknowns(self):
        #    If an unknown only exists in a single cell, get it!
        uniqueUnknowns = []
        if not self.solved:
            allValues = self.values()
            k = {}
            for value in allValues:
                k[value] = []
                for el in self.elements:
                    possibles = el.getPossibles()
                    if value in possibles:
                        k[value].append((value, el))
            for elements in k.values():
                if len(elements)==1:
                    uniqueUnknowns.append(elements[0])
        return uniqueUnknowns
    def getSingleDimPossibles(self):
        #   Get all possibles that in a single row/col.
        result = []
        for el in self.elements:
            if len(el.getPossibles())>1:
                result.append(el)
        rows = {}
        cols = {}
        unknowns = self.unknowns()
        if len(result)>0:
            for unknown in unknowns:
                rows[unknown] = []
                cols[unknown] = []
                for (_element) in result:
                    rows[unknown].append(_element.row)
                    cols[unknown].append(_element.col)
            for unknown in unknowns:
                r = Set(rows[unknown])
                if len(r)>1:
                    del rows[unknown]
                c = Set(cols[unknown])
                if len(c)>1:
                    del cols[unknown]
        #    Now we have the unique rows and cols we can work with:
        return (rows, cols)
    def getUnknownElements(self):
        unknownElements = []
        for el in self.elements:
            if not el.hasValue():
                unknownElements.append(el)
        return unknownElements

if __name__ == '__main__':
    pass
