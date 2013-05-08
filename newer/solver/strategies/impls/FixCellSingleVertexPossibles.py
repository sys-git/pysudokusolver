'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from sets import Set

class FixCellSingleVertexPossibles(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixCellSingleVertexPossibles"
    difficulty = StrategyDifficulty.EASY+4
    def __call__(self, model):
        for cell in model.cells:
            cellsR = model.getCellsForRow(cell)
            cellsC = model.getCellsForCol(cell)
            knowns = cell.knowns()
            for known in knowns:
                (row, col) = cell.coords(known)
                for c in cellsR:
                    for element in c.getRow(row):
                        possibles = element.getPossibles()
                        element.setPossibles(possibles-Set([known]))
                for c in cellsC:
                    for element in c.getCol(col):
                        possibles = element.getPossibles()
                        element.setPossibles(possibles-Set([known]))
