'''
Created on Mar 29, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.URef import URef
from newer.models.data import data
from newer.models.helper import helper
from newer.models.iModelNotifications import iModelNotifications
from sets import Set

class element(helper):
    NAME = "element"
    def __init__(self, row, col, size, values=[]):
        super(element, self).__init__(row, col, size)
        self._data = data(self.values())
        self._offsetRow = 0
        self._offsetCol = 0
    def _getUref(self):
        return URef(element.NAME, self._size, self.row, self.col, self._offsetRow, self._offsetCol)
    def getValue(self, type_=data.COMP):
        return self._data.getValue(type_)
    def setValue(self, value, type_=data.COMP):
        if value!=self.getValue(type_):
            self._data.setValue(type_, value)
            if value!=None:
                self.solved = True
                self.setPossibles()
            self._notifyListener(self.NAME, iModelNotifications.UPDATE(), self.uRef)
    def getPossibles(self, type_=data.COMP):
        return Set(self._data.getPossibles(type_))
    def setPossibles(self, possibles=[], type_=data.COMP):
        if Set(possibles)!=self.getPossibles(type_):
            self._data.setPossibles(type_, possibles)
            if self.hasUniquePossible(type_):
                self.setValue(list(self.getPossibles(type_))[0], type_)
            self._notifyListener(self.NAME, iModelNotifications.UPDATE(), self.uRef)
    def hasValue(self, type_=data.COMP):
        return self.getValue(type_)!=None
    def hasPossibles(self, type_=data.COMP):
        return len(self.getPossibles(type_))>0
    def hasUniquePossible(self, type_=data.COMP):
        return len(self.getPossibles(type_))==1
    def __str__(self):
        s = []
        v = self.getValue()
        if v!=None:
            s.append("Value[%(V)s]"%{"V":v})
        else:
            p = self.getPossibles()
            s.append("Poss:"+str(p))
        return " ".join(s)
    def update(self, element):
        if not self.hasValue():
            value = element.getValue()
            self.setValue(value)
        if (self.row!=element.row) or (self.col!=element.col):
            raise ValueError((self.row, self.col), (element.row, element.col))
        if self.hasPossibles():
            #    Keep the common subset:
            pMoi = self.getPossibles()
            pOther = element.getPossibles()
            removedValues = Set(self.xvalues())-pOther
            pMoi = pMoi-removedValues
            self.setPossibles(pMoi)
    def fix(self, knowns=[]):
        if not self.hasValue():
            possibles = self.getPossibles()
            newPossibles = possibles-Set(knowns)
            self.setPossibles(newPossibles)
    def serialize(self):
        params = {"state": self._state,
                  "row": self.row,
                  "col": self.col,
                  "size": self._size,
                  "offsetRow": self._offsetRow,
                  "offsetCol": self._offsetCol,
                  "data": self._data.serialize()}
        return params
    @staticmethod
    def deserialize(stream):
        el = element(stream["row"], stream["col"], stream["size"])
        el._state = stream["state"]
        el._offsetRow = stream["offsetRow"]
        el._offsetCol = stream["offsetCol"]
        el._data = data.deserialize(stream["data"])
        el.notDirty()
        return el
    def knowns(self):
        knowns = []
        if self.hasValue():
            knowns.append(self.getValue())
        return Set(knowns)
    def notification(self, who, event=None, args=None):
        try:
            if self._notifying==True:
                return
            self._notifying = True
            try:
                super(element, self).notification(who, event, args)
                self.fix()
            finally:
                self._notifying = False
        finally:
            self._notifyParentListener(who, event, args)

if __name__ == '__main__':
    pass
