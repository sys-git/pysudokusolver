'''
Created on Apr 16, 2013

@author: francis.horsman:gmail.com
'''

class URef(object):
    def __init__(self, name, size, row, col, offsetRow=0, offsetCol=0):
        self.name = name
        self.size = size
        self.row = row
        self.col = col
        self.offsetRow = offsetRow
        self.offsetCol = offsetCol
    def getAbsRow(self):
        return self.row + self.offsetRow
    def getAbsCol(self):
        return self.col + self.offsetCol
    absRow = property(getAbsRow)
    absCol = property(getAbsCol)
    def __str__(self):
        s = []
        args = {"N":self.name,
                "S":self.size,
                "R":self.row,
                "C":self.col,
                "OR":self.offsetRow,
                "OC":self.offsetCol,
                "TR":(self.offsetRow+self.row),
                "TC":(self.offsetCol+self.col),
                }
        s.append("URef[%(S)s][%(N)s]"%args)
        s.append(":")
        s.append("(%(R)s+%(OR)s,"%args)
        s.append("%(C)s+%(OC)s)"%args)
        s.append("=")
        s.append("(%(TR)s, %(TC)s)"%args)
        return " ".join(s)