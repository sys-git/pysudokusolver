'''
Created on Apr 24, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.grid import grid
from newer.solver.strategies.impls.Xwing import Xwing
import sys
import traceback
import unittest

class TestXWing(unittest.TestCase):
    def setUp(self):
        newData  = [[1, None, None,     None, None, None,   5, 6, 0],
                   [4, 0, 2,            None, 5, 6,         1, None, 8], 
                   [None, 5, 6,         1, None, 0,         2, 4, None], 
                   [None, None, 0,      6, 4, None,         8, None, 1],
                   [None, 6, 4,         None, 1, None,      None, None, None],
                   [2, 1, 8,            None, 3, 5,         6,  None, 4],
                   [None, 4, None,      5, None, None,      None, 1, 6],
                   [0, None, 5,         None, 6, 1,         4, None, 2],
                   [6, 2, 1,            None, None, None,   3, None, 5]]
        self.model = grid(3)
        self.model.data = newData
        self.model.fix()
        self.x = Xwing()
        print self.model.prettyprint()
    def test(self):
        sys.stderr.write("Go...\n")
        try:
            self.x(self.model)
        except Exception, _e:
            print traceback.format_exc()
        else:
            pass
        sys.stderr.write("...done!\n")

if __name__ == '__main__':
    unittest.main()
