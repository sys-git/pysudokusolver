'''
Created on Mar 29, 2013

@author: francis.horsman:gmail.com
'''
from sets import Set
import copy

class data(object):
    #    Type:
    USER = 0
    COMP = 1
    #    What:
    VALUE = 0
    POSSIBLES = 1
    def __init__(self, possibles=[]):
        self._data = {data.USER:{}, data.COMP:{}}
        self._data[data.USER][data.VALUE] = None
        self._data[data.USER][data.POSSIBLES] = []
        self._data[data.COMP][data.VALUE] = None
        self._data[data.COMP][data.POSSIBLES] = possibles
    def user(self):
        return self._data[data.USER]
    def comp(self):
        return self._data[data.COMP]
    def getValue(self, type_):
        return self._data[type_][data.VALUE]
    def setValue(self, type_, value):
        self._data[type_][data.VALUE] = value
    def getPossibles(self, type_):
        return self._data[type_][data.POSSIBLES]
    def setPossibles(self, type_, values=[]):
        self._data[type_][data.POSSIBLES] = values
    def serialize(self):
        d = copy.deepcopy(self._data)
        for i in [data.USER, data.COMP]:
            for k in [data.POSSIBLES]:
                if d[i][k]!=None:
                    try:
                        d[i][k] = list(d[i][k])
                    except Exception, _e:
                        d[i][k] = None
        return d
    @staticmethod
    def deserialize(stream):
        d = data()
        d._data = stream
        try:
            for i in [data.USER, data.COMP]:
                for k in [data.POSSIBLES]:
                    if stream[i][k]!=None:
                        try:
                            d._data[i][k] = Set(d._data[i][k])
                        except Exception, _e:
                            d._data[i][k] = None
        except Exception, _e:
            raise
        return d

if __name__ == '__main__':
    pass
