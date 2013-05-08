'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

class StrategyDifficulty(object):
    EASY = 0
    MED = 100
    HARD = 200
    FIENDISH = 300
    UNBELIEVABLE = 400
    UNKNOWN = 100
    @staticmethod
    def _getStrategyDict():
        d = {}
        for n in dir(StrategyDifficulty):
            if n.isupper():
                d[getattr(StrategyDifficulty, n)] = {}
        return d
