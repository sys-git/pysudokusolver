'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty

class FixGrid(object):
    r"""@author: francis.horsman@gmail.com
    """
    name = "FixGrid"
    difficulty = StrategyDifficulty.EASY+1
    def __call__(self, model):
        model.fix()
