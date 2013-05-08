'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''

from newer.solver.Result import Result

class UnSolveable(Result):
    def __str__(self):
        return "UnSolveable"

