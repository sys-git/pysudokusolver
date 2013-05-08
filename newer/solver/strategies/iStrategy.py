'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

class iStrategy(object):
    #    Base class for all strategies.
    def __str__(self):
        return self.name
    def __init__(self, checkAbort, solved, unsolvable):
        self.solved = solved
        self.unsolvable = unsolvable
        self._checkAbort = checkAbort
