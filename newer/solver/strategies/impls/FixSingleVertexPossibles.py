'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from sets import Set

class FixSingleVertexPossibles(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixSingleVertexPossibles"
    difficulty = StrategyDifficulty.EASY+8
    def __call__(self, model):
        r"""
        For each cell, for each value, if all value possibles in a single row/col then:
        remove this value as a possible from adjacent cells in this row/col.
        """
        def getAdjacentCells(cell):
            (rows, cols) = cell.getSingleDimPossibles()
            if len(rows.keys())==0 and len(cols.keys())==0:
                return (({}, {}), ([], []))
            cellsR = model.getCellsForRow(cell)
            cellsC = model.getCellsForCol(cell)
            for duplicateCell in Set(cellsR)&Set(cellsC):
                cellsC.remove(duplicateCell)
                cellsR.remove(duplicateCell)
                cellsC.append(duplicateCell)
            return ((rows, cols), (cellsR, cellsC))
        def handleCellRows(cell, cells, rows):
            for possibleValue, row in rows.items():
                possibleValue = Set([possibleValue])
                row = list(Set(row))[0]
                #    Remove possibleValue from cells in col.
                for cell in cells:
                    for col in xrange(cell._size):
                        el = cell.getElementAt(row, col)
                        possibles = el.getPossibles()
                        el.setPossibles(possibles-possibleValue)
        def handleCellCols(cell, cells, cols):
            for possibleValue, col in cols.items():
                possibleValue = Set([possibleValue])
                col = list(Set(col))[0]
                #    Remove possibleValue from cells in col.
                for cell in cells:
                    for row in xrange(cell._size):
                        el = cell.getElementAt(row, col)
                        possibles = el.getPossibles()
                        el.setPossibles(possibles-possibleValue)
        for cell in model.cells:
            self._checkAbort()
            ((rows, cols), (cellsR, cellsC)) = getAdjacentCells(cell)
            handleCellRows(cell, cellsR, rows)
            handleCellCols(cell, cellsC, cols)
