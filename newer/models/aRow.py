'''
Created on Apr 5, 2013

@author: francis.horsman:gmail.com
'''

from sets import Set
import collections

class _aList(list):
    def __init__(self, elements):
        self._elements = elements
        super(_aList, self).__init__(tuple(elements, ))
    def knowns(self):
        knowns = []
        for el in self._elements:
            knowns.extend(el.knowns())
        return Set(knowns)
    def unknowns(self):
        return [(i, index) for index, i in enumerate(self) if not i.hasValue()]
    def unknown(self):
        a = Set(xrange(self._elements[0]._maxSize))
        unknowns = a - self.knowns()
        return unknowns
    def unknownCounts(self):
        counts = collections.defaultdict(list)
        unknowns = self.unknown()
        for unknown in unknowns:
            for element in self._elements:
                if not element.hasValue():
                    possibles = element.getPossibles()
                    if unknown in possibles:
                        counts[unknown].append(element.uRef)
        for key, value in counts.items():
            counts[key] = list(Set(value))
        return counts
    def countPossibleValues(self):
        ll = [list(i.getPossibles()) for i in self if not i.hasValue()]
        totals = []
        [totals.extend(what) for what in ll]
        c = collections.Counter(totals)
        return c
    def getUnknownElements(self):
        unknownElements = []
        for el in self._elements:
            if not el.hasValue():
                unknownElements.append(el)
        return unknownElements

class aCol(_aList):
    pass

class aRow(_aList):
    pass
