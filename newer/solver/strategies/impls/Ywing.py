'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.aRow import aRow, aCol
from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from sets import Set
import collections

class Ywing(object):
    r"""@see: http://www.sudokuwiki.org/Y_Wing_Strategy
    The rule is:
        When:
            2 elements in a vertex share a possibleValue AND
            altVertex for each vertex share the other-possibleValue at the same
            altVertex coords.
        Then:
            remove the other-PossibleValue where the 2 vertexes meet.
    Visa Versa
    """
    name = "Ywing"
    difficulty = StrategyDifficulty.MED+2
    def __call__(self, model):
        print model.prettyprint()
        vertex = collections.namedtuple("vertex", ["aVertex", "getElementVertex", "findElementsForAltVertex"])
        v1 = vertex(aVertex=aRow, getElementVertex="getElementRows", findElementsForAltVertex="findElementsForCol")
        v2 = vertex(aVertex=aCol, getElementVertex="getElementCols", findElementsForAltVertex="findElementsForRow")
        self.method(model, v1)
        self.method(model, v2)
    def method(self, model, vertex):
        for row in getattr(model, vertex.getElementVertex)():
            row = vertex.aVertex(row)
            unknownCounts = row.unknownCounts()
            for i, j in unknownCounts.items():
                if len(j)!=2:
                    del unknownCounts[i]
            for possibleValue, urefs in unknownCounts.items():
                el1 = model.findElement(urefs[0].absRow, urefs[0].absCol)
                el2 = model.findElement(urefs[1].absRow, urefs[1].absCol)
                #    If possibles are identical, move on!
                p1 = el1.getPossibles()
                p2 = el2.getPossibles()
                if p1==p2:
                    continue
                if len(p1)!=2 or len(p2)!=2:
                    continue
                #    Get the alt-vertex for each el in urefs:
                col1 = getattr(model, vertex.findElementsForAltVertex)(urefs[0].absCol)
                col2 = getattr(model, vertex.findElementsForAltVertex)(urefs[1].absCol)
                #    Does possibleValue occur in both cols at the same row
                for searchFor in [list(el1.getPossibles()-Set([possibleValue]))[0],
                                  list(el2.getPossibles()-Set([possibleValue]))[0]]:
                    for x in xrange(model._maxSize):
                        i = col1[x]
                        j = col2[x]
                        if not i.hasValue() and not j.hasValue():
                            p1 = i.getPossibles()
                            p2 = j.getPossibles()
                            if p1==p2:
                                continue
                            if len(p2)!=2:
                                continue
                            if searchFor in p1 and searchFor in p2:
                                altValue = el2.getPossibles()-Set([searchFor])
                                #    Is altValue in p2?
                                if altValue in p2:
                                    #    Found one!
                                    print "Found redundant value: '%s' in '%s'"%(searchFor, p1)
                                    poss = p1-Set(searchFor)
                                    i.setPossibles(poss)
