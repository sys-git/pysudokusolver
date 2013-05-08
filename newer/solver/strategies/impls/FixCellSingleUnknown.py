'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty

class FixCellSingleUnknown(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixCellSingleUnknown"
    difficulty = StrategyDifficulty.EASY+2
    def __call__(self, model):
        for cell in model.cells:
            el, value = cell.unknown()
            if el and value:
                el.setValue(value)
