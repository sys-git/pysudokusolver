'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from newer.solver.strategies.impls.fixVertexPossibles import fixVertexPossibles

class FixRowVertexPossibles(fixVertexPossibles):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixRowVertexPossibles"
    difficulty = StrategyDifficulty.EASY+7
    def __call__(self, model):
        return self._rolCol(model, "elementRows", "row", "col")
