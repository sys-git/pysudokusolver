'''
Created on 21 Mar 2013

@author: francis.horsman:gmail.com
'''

class Result(Exception):
    def __init__(self, model, tId=None, args=None):
        self.tId = tId
        try:
            s = model.serialize()
        except Exception, _e:
            s = model
        super(Result, self).__init__(s)
        self._model = s
        self._args = args
    def _getModel(self):
        return self._model
    def _getArgs(self):
        return self._args
    model = property(_getModel)
    args = property(_getArgs)
