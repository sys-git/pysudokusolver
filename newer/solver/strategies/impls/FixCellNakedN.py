'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.aRow import aRow, aCol
from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from sets import Set
import collections
import itertools

class FixCellNakedN(object):
    r"""@author: francis.horsman@gmail.com
    If a cell/vertex contains n pairs of same n possibles, then remove these
    possibles from other elements in cell/vertex.
    """
    name = "FixCellNakedN"
    difficulty = StrategyDifficulty.EASY+9
    def __call__(self, model):
        for digits in xrange(2, model._maxSize):
#             print model.prettyprint()
            #    Work on cells first:
            for cell in model.cells:
                unknownElements = cell.getUnknownElements()
                self._work(unknownElements, digits)
#                 print model.prettyprint()
            #    Now work on rows:
            for row in model.getElementRows():
                row = aRow(row)
                unknownElements = row.getUnknownElements()
                self._work(unknownElements, digits)
#                 print model.prettyprint()
            #    Now work on cols:
            for col in model.getElementCols():
                col = aCol(col)
                unknownElements = col.getUnknownElements()
                self._work(unknownElements, digits)
#                 print model.prettyprint()
#             print model.prettyprint()
    def _work(self, unknownElements, digits):
        for i, el in enumerate(unknownElements):
            possibles = el.getPossibles()
            r"""for all combos (n>=2) of possibles,
            if the combo exists in only n elements and each element
            of the combo does not exist in the rest of the elements
            then remove the other possibles from these combo cells AND
            remove the combo from all other elements's possibles!
            """
            if len(possibles)==digits:
                items = collections.defaultdict(list)
                def getCombos(poss, rr):
                    for permutation in itertools.combinations(poss, rr):
                        print permutation
                        yield permutation
                for combo in getCombos(possibles, digits):
                    comboValue = list(combo)
                    items[combo].append(el)
                    #    Look ahead ONLY:
                    for ii in xrange(i+1, len(unknownElements)):
                        el1 = unknownElements[ii]
                        possibles1 = el1.getPossibles()
                        if len(possibles1)==digits:
                            comboPossibles = Set(comboValue)
                            if (comboPossibles&possibles1==comboPossibles):
                                items[combo].append(el1)
                #    See if any combo of len(combo) appears only len(combo)
                #    times in items.
                for (combo, elements) in items.items():
                    lenCombo = len(combo)
                    if len(elements)==lenCombo:
                        #    Found one!
                        combo = Set(combo)
                        #    Now remove the other possibles from each of elements:
                        for el2 in elements:
                            el2.setPossibles(combo)
                        #    Now remove the combo from all other elements in unknownElements.
                        for el2 in unknownElements:
                            if el2 not in elements:
                                poss = el2.getPossibles()
                                poss1 = poss-combo
                                if poss1!=poss:
                                    print "Combo: '%s' found in '%s' elements: '%s'"%(combo, lenCombo, elements)
                                    el2.setPossibles(poss1)
                                    return
                    pass
                pass
            pass
        pass