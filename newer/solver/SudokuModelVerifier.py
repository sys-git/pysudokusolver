'''
Created on 14 Mar 2013

@author: francis.horsman:gmail.com
'''
from newer.solver.Solved import Solved
from newer.solver.Solving import Solving
from newer.solver.UnSolveable import UnSolveable


class SudokuModelVerifier(object):
    def __init__(self, model):
        self._model = model
        self()
    def __call__(self):
        #    Currently, this is the only way to check that the puzzle is unsolvable statically:
        if self._model.unsolvable:
            raise UnSolveable(self._model)
        #    Now check the values are all correct:
        try:
            self._validateRows()
            self._validateCols()
            self._validateCells()
        except Exception, _e:
            raise Solving(self._model)
        raise Solved(self._model)
    def _validateRows(self):
        for row in self._model.elementRows: 
            elements = [e.getValue() for e in row]
            self._checkUniqueElements(elements)
    def _validateCols(self):
        for col in self._model.elementCols: 
            elements = [e.getValue() for e in col]
            self._checkUniqueElements(elements)
    def _validateCells(self):
        for cell in self._model.cells:
            elements = [e.getValue() for e in cell.elements]
            self._checkUniqueElements(elements)
    def isValidated(self):
        try:
            self.validate()
        except ValueError, _e:
            return False
        return True
    def checkValidation(self):
        if self.isValidated():
            raise Solved(self._model)
    def _checkUniqueElements(self, elements, eCount=1):
        if eCount<1:
            raise ValueError("Invalid eCount: '%(E)s', must be >= 1."%{"E":eCount})
        values = {}
        for value in elements:
            if value==None:
                raise Solving(self._model)
            if value not in values.keys():
                values[value] = 0
            values[value] += 1
        for value, count in values.items():
            if values[value]>eCount:
                raise ValueError("Too many occurances of value: '%(V)s', expecting '%(C)s' occurances only, but got: '%(G)s'."%{"V":value, "C":eCount, "G":count})

