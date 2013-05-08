'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from newer.solver.strategies.impls.fixVertexPossibles import fixVertexPossibles

class FixColVertexPossibles(fixVertexPossibles):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixColVertexPossibles"
    difficulty = StrategyDifficulty.EASY+6
    def __call__(self, model):
        return self._rolCol(model, "elementCols", "col", "row")
