'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty

class FixCellSingleUnknownValue(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixCellSingleUnknownValue"
    difficulty = StrategyDifficulty.EASY+3
    def __call__(self, model):
        for cell in model.cells:
            elements = cell.uniqueUnknowns()
            for (value, element) in elements:
                element.setValue(value)
