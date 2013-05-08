'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.strategies.StrategyDifficulty import StrategyDifficulty
from newer.solver.strategies.iStrategy import iStrategy
import os
import sys
import traceback

class StrategiesFactory(object):
    def __init__(self, model, checkAbort, solved, unsolvable):
        self._model = model
        self._checkAbort = checkAbort
        self._solved = solved
        self._unsolvable = unsolvable
        self._cache = StrategiesFactory.createStrategies(StrategiesFactory.loadStrategies(), self._model, self._checkAbort, self._solved, self._unsolvable)
    def __call__(self):
        #    Get the strategies pipeline list ordered by difficulty (easiest first!)
        pipeline = []
        difficulties = self._cache.keys()
        difficulties.sort()
        for difficulty in difficulties:
            for _name, strategy in self._cache[difficulty].items():
                pipeline.append(strategy)
        return pipeline
    @staticmethod
    def createStrategies(strategies, model, checkAbort, solved, unsolvable):
        cache = StrategyDifficulty._getStrategyDict()
        for s in strategies:
            try:
                if type(s)==type:
                    strategy = s(checkAbort, solved, unsolvable)
                    try:
                        name = strategy.name
                    except:
                        print "strategy has no name: %(S)s"%{"S":strategy}
                        raise
                    try:
                        difficulty = strategy.difficulty
                    except:
                        print "strategy has no difficulty, making 'unknown': %(S)s"%{"S":strategy}
                        difficulty = StrategyDifficulty.UNKNOWN
                    if difficulty not in cache.keys():
                        cache[difficulty] = {}
                    cache[difficulty][name] = strategy
            except Exception, _e:
                traceback.print_exc()
        return cache
    @staticmethod
    def loadStrategies():
        strategies = []
        path = os.path.join(os.path.dirname(__file__), "impls")
        modules = [f for f in os.listdir(path) if not os.path.isdir(f)==True
                   and os.path.splitext(f)[1]==".py"
                   and f[0].isupper()
#                     and f[0]!="X"
                   ]
        #    Now load the modules from 'modules':
        sys.path.insert(0, path)
        for m in modules:
            name = os.path.basename(m)
            name = os.path.splitext(name)[0]
            strategy = StrategiesFactory.importModule(name, name)
            if iStrategy not in strategy.__bases__:
                strategy = type(name, (strategy, iStrategy, object), {})
            strategies.append(strategy)
        return strategies
    @staticmethod
    def importModule(where, what):
        _module = __import__(where, globals(), locals(), [what], -1)
        _type = getattr(_module, what)
        return _type
    @staticmethod
    def _importModuleName(name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

if __name__ == '__main__':
    sf = StrategiesFactory(None, None, None, None)
    for i in sf():
        print i
