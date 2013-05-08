'''
Created on Apr 24, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.grid import grid
from newer.solver.strategies.impls.FixCellNakedN import \
    FixCellNakedN
import sys
import traceback
import unittest

class TestFixCellNakedDoubles(unittest.TestCase):
    def setUp(self):
        newData  = [[4, None, None,     None, None, None,   9, 3, 8],
                   [None, 3, 2,         None, 9, 4,         1, None, None], 
                   [None, 9, 5,         3, None, None,      2, 4, None],
                   [3, 7, None,         6, None, 9,         None, None, 4],
                   [5, 2, 9,            None, None, 1,      6,  7, 3],
                   [6, None, 4,         7, None, 3,         None, 9, None],
                   [8, 5, 7,            None, None, 8,      3, None, None],
                   [None, None, 3,      9, None, None,      4, None, None],
                   [2, 4, None,         None, 3, None,      7, None, 9]]
        self.model = grid(3)
        self.model.data = newData
        self.model.fix()
        self.x = FixCellNakedN()
        print self.model.prettyprint()
    def test(self):
        sys.stderr.write("Go...\n")
        try:
            self.x(self.model)
        except Exception, _e:
            print traceback.format_exc()
        else:
            pass
        print self.model.prettyprint()
        sys.stderr.write("...done!\n")

if __name__ == '__main__':
    unittest.main()
