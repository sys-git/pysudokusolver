'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''

class Custom(object):
    def __init__(self, who, tId=None, args=None):
        self._who = who
        self.tId = tId
        self._args = args
    def __str__(self):
        return "Custom: '%(D)s'."%{"D":self._args}
    def getArgs(self):
        return self._args
    def getWho(self):
        return self._who
    args = property(getArgs)
    who = property(getWho)
