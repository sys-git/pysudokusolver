'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.aRow import aRow, aCol
from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from sets import Set
import collections

class Xwing(object):
    r"""@see: http://www.sudokuwiki.org/X_Wing_Strategy
    The rule is:
        When:
            there are only two possible cells for a value in each of two
        different rows, and these candidates lie also in the same columns,
        then:
            all other candidates for this value in the columns can be eliminated.
    Visa Versa
    """
    name = "xwing"
    difficulty = StrategyDifficulty.MED+1
    def __call__(self, model):
        vertex = collections.namedtuple("vertex", ["aVertex", "findElementsForVertex", "absAltVertex", "aAltVertex", "findElementsForAltVertex", "absVertex", "altVertexes"])
        v1 = vertex(aVertex=aRow, findElementsForVertex="findElementsForRow", absAltVertex="absCol", aAltVertex=aCol, findElementsForAltVertex="findElementsForCol", absVertex="absRow", altVertexes="cols")
        v2 = vertex(aVertex=aCol, findElementsForVertex="findElementsForCol", absAltVertex="absRow", aAltVertex=aRow, findElementsForAltVertex="findElementsForRow", absVertex="absCol", altVertexes="rows")
        self._execute(model, v1, v2)
        self._execute(model, v2, v1)
    def _execute(self, model, vertex, altVertex):
        print model.prettyprint()
        allXwings = collections.defaultdict(list)
        for value in model.unknowns():
            for rr in xrange(model._maxSize):
                xwings = collections.defaultdict(list)
                cls = vertex.aVertex
                r = cls(getattr(model, vertex.findElementsForVertex)(rr))
                unknownCounts = r.unknownCounts()
                if value in unknownCounts.keys():
                    if len(unknownCounts[value])==2:
                        #    Now look in the other vertex (cols) for these
                        #    coords.
                        altVertexs = [getattr(elUref, vertex.absAltVertex) for elUref in unknownCounts[value]]
                        #    Get the 2 columns and see if any of 'value' appear in the
                        #    columns on the same row index.
                        altVertexs0 = vertex.aAltVertex(getattr(model, vertex.findElementsForAltVertex)(altVertexs[0]))
                        altVertexs1 = vertex.aAltVertex(getattr(model, vertex.findElementsForAltVertex)(altVertexs[1]))
                        try:
                            uc0 = altVertexs0.unknownCounts()
                            uc1 = altVertexs1.unknownCounts()
                            if ((len(uc0[value])>=2) and
                                (len(uc1[value])>=2) ):
                                #    Now see if the index's overlap on at least 2:
                                #    At least 2 uRef's from uc0 should be same row as uc1:
                                vertexes_ = []
                                for i in uc0[value]:
                                    iR = getattr(i, vertex.absVertex)
                                    for k in uc1[value]:
                                        kR = getattr(k, vertex.absVertex)
                                        if iR==kR:
                                            vertexes_.append(([getattr(i, vertex.absAltVertex), getattr(k, vertex.absAltVertex)], iR))
                                #    Now make sure 'value' is only present twice in each
                                #    rows' possible values.
                                for (_Altvertex, _vertex) in vertexes_:
                                    tVertex = vertex.aVertex(getattr(model, vertex.findElementsForVertex)(_vertex))
                                    c = tVertex.countPossibleValues()
                                    if c[value]==2:
                                        if _vertex not in xwings[value]:
                                            xwings[value].append(_vertex)
                        except Exception, _e:
                            #    no luck!
                            pass
                voo = Set(xwings[value])
                if voo not in allXwings[value]:
                    allXwings[value].append(voo)
        newXwings = collections.defaultdict(list)
        for key, value in allXwings.items():
            i = [p for p in value if len(list(p))>0]
            if len(i)>0:
                ii = [p for p in i if len(p)==2]
                if len(ii)>0:
                    newXwings[key].append(ii)
        #    Now fix the xwings:
        for value, i in newXwings.items():
            for k in i:
                for j in k:
                    j = list(j)
                    #    Got an xwing in VERTEX, so get the ALT_VERTEX for 'value':
                    r = j[0]
                    row = vertex.aVertex(getattr(model, vertex.findElementsForVertex)(r))
                    #    Get the ALT_VERTEXS for both possibleValues=value:
                    cols = []
                    for col, el in enumerate(row):
                        if not el.hasValue():
                            possibles = el.getPossibles()
                            if value in possibles:
                                cols.append(vertex.aAltVertex(getattr(model, vertex.findElementsForAltVertex)(col)))
                    #    Now remove 'value' from the ALT_VERTEXS possibles EXCEPT from VERTEXS in j.
                    for col in cols:
                        for index, el in enumerate(col):
                            if index not in j:
                                if not el.hasValue():
                                    possibles = el.getPossibles()
                                    newPossibles = possibles-Set([value])
                                    el.setPossibles(newPossibles)
                    print "Fixed xwing for value: %s in cols: %s"%(value, j)
    def __callOLD__(self, model, vertex, altVertex):
        print model.prettyprint()
        allXwings = collections.defaultdict(list)
        for value in model.unknowns():
            for rr in xrange(model._maxSize):
                xwings = collections.defaultdict(list)
                r = aRow(model.findElementsForRow(rr))
                unknownCounts = r.unknownCounts()
                if value in unknownCounts.keys():
                    if len(unknownCounts[value])==2:
                        #    Now look in the other vertex (cols) for these
                        #    coords.
                        cols = [elUref.absCol for elUref in unknownCounts[value]]
                        #    Get the 2 columns and see if any of 'value' appear in the
                        #    columns on the same row index.
                        cols0 = aCol(model.findElementsForCol(cols[0]))
                        cols1 = aCol(model.findElementsForCol(cols[1]))
                        try:
                            uc0 = cols0.unknownCounts()
                            uc1 = cols1.unknownCounts()
                            if ((len(uc0[value])>=2) and
                                (len(uc1[value])>=2) ):
                                #    Now see if the index's overlap on at least 2:
                                #    At least 2 uRef's from uc0 should be same row as uc1:
                                rows_ = []
                                for i in uc0[value]:
                                    iR = i.absRow
                                    for k in uc1[value]:
                                        kR = k.absRow
                                        if iR==kR:
                                            rows_.append(([i.absCol, k.absCol], iR))
                                #    Now make sure 'value' is only present twice in each
                                #    rows' possible values.
                                for (cols, row) in rows_:
                                    tRow = aRow(model.findElementsForRow(row))
                                    c = tRow.countPossibleValues()
                                    if c[value]==2:
#                                         print "'%s' is present twice in row: %s"%(value, row)
                                        if row not in xwings[value]:
                                            xwings[value].append(row)
                        except Exception, _e:
                            #    no luck!
                            pass
                voo = Set(xwings[value])
                if voo not in allXwings[value]:
                    allXwings[value].append(voo)
        newXwings = collections.defaultdict(list)
        for key, value in allXwings.items():
            i = [p for p in value if len(list(p))>0]
            if len(i)>0:
                ii = [p for p in i if len(p)==2]
                if len(ii)>0:
                    newXwings[key].append(ii)
#                     print "found: value '%s' = rows: '%s'"%(key, i)
#                     for k in i:
#                         print "> %s"%k
        #    Now fix the xwings:
        for value, i in newXwings.items():
            for k in i:
                for j in k:
                    j = list(j)
                    #    Got an xwing in rows, so get the cols for 'value':
#                     print "value: %s in rows: %s"%(value, j)
                    r = j[0]
                    row = aRow(model.findElementsForRow(r))
                    #    Get the cols for both possibleValues=value:
                    cols = []
                    for col, el in enumerate(row):
                        if not el.hasValue():
                            possibles = el.getPossibles()
                            if value in possibles:
                                cols.append(aCol(model.findElementsForCol(col)))
#                     print cols
                    #    Now remove 'value' from the cols possibles EXCEPT
                    #    from rows in j.
                    for col in cols:
                        for index, el in enumerate(col):
                            if index not in j:
                                if not el.hasValue():
                                    possibles = el.getPossibles()
                                    newPossibles = possibles-Set([value])
                                    el.setPossibles(newPossibles)
                    print "Fixed xwing for value: %s in cols: %s"%(value, j)


