'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.aRow import aRow, aCol
from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty

class FixCellPossiblesFromAdjacentCells(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixCellPossiblesFromAdjacentCells"
    difficulty = StrategyDifficulty.EASY+5
    def __call__(self, model):
        #    For each cell, for each value for each dim:
        #    remove value as a possible from each adjacent cell.
        for cell in model.cells:
            self._checkAbort()
            cellsR = model.getCellsForRow(cell)
            cellsC = model.getCellsForCol(cell)
            for index, row in enumerate(cell.rows):
                known = aRow(row).knowns()
                if len(list(known))>0:
                    self._checkAbort()
                    for cell_ in cellsR:
                        row_ = cell_.getRow(index)
                        for element in row_:
                            if not element.hasValue():
                                possibles = element.getPossibles()
                                element.setPossibles(possibles-known)
            for index, col in enumerate(cell.cols):
                known = aCol(col).knowns()
                if len(list(known))>0:
                    for cell_ in cellsC:
                        self._checkAbort()
                        col_ = cell_.getCol(index)
                        for element in col_:
                            if not element.hasValue():
                                possibles = element.getPossibles()
                                element.setPossibles(possibles-known)
