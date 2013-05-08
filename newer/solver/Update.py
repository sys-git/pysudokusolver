'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''

class Update(object):
    def __init__(self, data, tId=None, args=None):
        self.tId = tId
        self._data = data
        self._args = args
    def __str__(self):
        return "Update: '%(D)s'."%{"D":self._data}
    def _getData(self):
        return self._data
    def _getArgs(self):
        return self._args
    data = property(_getData)
    args = property(_getArgs)
