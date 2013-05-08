'''
Created on 14 Mar 2013

@author: francis.horsman:gmail.com
'''

from Queue import Empty
from multiprocessing.synchronize import RLock, Event, Semaphore
from newer.models.cell import cell
from newer.models.element import element
from newer.models.grid import grid
from newer.models.iModelNotifications import iModelNotifications
from newer.solver.AbortAck import AbortAck
from newer.solver.Aborted import Aborted
from newer.solver.Custom import Custom
from newer.solver.Solved import Solved
from newer.solver.Solving import Solving
from newer.solver.SudokuModelVerifier import SudokuModelVerifier
from newer.solver.UnSolveable import UnSolveable
from newer.solver.Update import Update
from newer.solver.impls.AsynchronousSolver import AsynchronousSolver
import threading
import time
import traceback
# import cPickle
#import unittest

class Context(object):
    def __init__(self, count, getModel, abort, lock):
        self._thread = None
        self._count = count
        self._getModel = getModel
        self._abort = abort
        self._lock = lock
        self._listeners = []

class Solver(object):
    UNSOLVED = -1
    SOLVED = 0
    SOLVING = 1
    UNSOLVABLE = 2
    r"""
    @attention: Always reference the model thus: solver.model.xxx
    """
    def __init__(self, model, count=1):
        self._lock = RLock()
        self._model = model
        #    Context:
        self._abort = Event()
        self._abort.clear()
        self._solvers = Context(count, self._getModel, self._abort, self._lock)
        self._isAborted = False
    def _getModel(self):
        with self.lock():
            return self._model
    model = property(_getModel)
    def __str__(self):
        pre="Unsolved"
        with self.lock():
            if len(list(self._model.unknowns()))==0:
                pre="> SOLVED < "
            return "\n".join(["%(PRE)sSolver:"%{"PRE":pre}, str(self._model)])
    def lock(self):
        return self._lock
    def serialize(self):
        #    Retrieve the model ready for storing:
        with self.lock():
            return self._model.serialize()
    def deserialize(self, data):
        #    Load the model ready for use:
        with self.lock():
            self._model = self.model.deserialize(data)
    def clone(self):
        with self.lock():
            try:
                self.abort()
            except Aborted, _e:
                pass
            self._abort.set()
            m = self.model.clone()
            self._isAborted = False
            return Solver(m)
    def solve(self):
        #    Solve it automagically!
        with self.lock():
            if self.model.solved:
                raise Solved(self.model)
            if self._solvers._thread!=None:
                raise Solving(self.model)
            #    Let the solving commence:
            self._solvers._thread = threading.Thread(target=self._solve)
            self._solvers._thread.setName("Solver.solving")
            self._solvers._thread.setDaemon(True)
            self._abort.set()
            self._solvers._thread.start()
    def isAborted(self):
        return (self._isAborted==True)
    def abort(self):
        #    Stop solving!
        with self.lock():
            self._abort.clear()
            if self._solvers._thread!=None:
                self._solvers._thread.join()
            self._isAborted = True
            raise Aborted()
    def _checkAbortAck(self):
        if self.isAborted():
            raise AbortAck()
    def data(self, data):
        with self._solvers._lock:
            self.model.data = data
    def _solve(self):
        print "Solver main loop running @ %(T)s"%{"T":time.time()}
        self._model.addParentListener(self)
        self._model.addListener(self)
        e = None
        solver = None
        try:
            solver = AsynchronousSolver(self._solvers, self._lock)
            while self._abort.is_set():
                try:
                    data = solver.get(block=True, timeout=1)
                except Empty:
                    continue
                else:
                    if isinstance(data, Update):
                        if data.data[0]==grid.NAME:
                            pass
                        elif data.data[0]==cell.NAME:
                            pass
                        elif data.data[0]==element.NAME:
                            pass
                        self.model.update(data.data[1])
                    elif isinstance(data, Custom):
                        self.notification(data.who, iModelNotifications.CUSTOM(), data.args)
        except UnSolveable, e:
            print "Solving impossible!"
            newModel = self.model.deserialize(e.model)
            self.model.update(newModel)
        except Solved, e:
            newModel = self.model.deserialize(e.model)
            self.model.update(newModel)
        except AbortAck, e:
            print "Solver abort ack, nothing to do!"
        except Exception, e:
            print "Solver main loop exception:\n%(T)s"%{"T":traceback.format_exc()}
        finally:
            err = ""
            if e!=None and not isinstance(e, (Solved, UnSolveable)):
                err = ":\n%(T)s"%{"T":traceback.format_exc()}
            del solver
            print "Solver main loop finished%(E)s"%{"E":err}
    def verify(self):
        #    Verify all is correct from a solving point of view:
        return self._verify()
    def _verify(self):
        return SudokuModelVerifier(self.model)
    def addListener(self, listener):
        self.removeListener(listener)
        self._solvers._listeners.append(listener)
    def removeListener(self, listener):
        try:
            self._solvers._listeners.remove(listener)
        except:
            pass
    def notification(self, who, event=None, args=None):
        events = [iModelNotifications.CUSTOM(), iModelNotifications.SOLVED(), iModelNotifications.UNSOLVABLE()]
        if event in events:
            for listener in self._solvers._listeners:
                try:
                    listener(who, event, args)
                except Exception, _e:
                    raise
        else:
            pass

def test(newData):
    sem = Semaphore(0)
    class _listener(object):
        def __init__(self, s):
            self._s = s
        def __call__(self, who, event, args=None):
            if who==grid.NAME:
                if event==iModelNotifications.SOLVED():
                    print "Test listener: SOLVED !"
                    self._s.release()
                elif event==iModelNotifications.UNSOLVABLE():
                    print "Test listener: UNSOLVABLE !"
                    self._s.release()
                elif event==iModelNotifications.CUSTOM():
                    print "Test listener: Custom event[%s]: %s"%(grid, args)
            else:
                print "Test listener non-grid WHO: '%(W)s', event: '%(E)s', args: '%(A)s'"%{"E":event, "W":who, "A":args}
    solver2 = Solver(grid(3))
    solver2.addListener(_listener(sem))
    solver2.data(newData)
    print solver2.model.prettyprint()
    timeStart = time.time()
    print "Go: %(T)s"%{"T":time.strftime("%H:%M:%S", time.localtime(timeStart))}
    print "Go: %(T)s"%{"T":time.time()}
    try:
        solver2.solve()
    except (Solved, Solving), _e:
        assert False
    else:
        assert True
    sem.acquire(block=True, timeout=20000)
    timeEnd = time.time()
    timeDelta = timeEnd-timeStart
    try:
        try:
            solver2.abort()
        except Aborted, _e:
            pass
        try:
            solver2.verify()
        except Solved, _e:
            assert True
        except UnSolveable, _e:
            assert False
        except Solving, _e:
            assert False
        else:
            assert False
    finally:
        print "Done: %(T)s"%{"T":time.strftime("%H:%M:%S", time.localtime(timeEnd))}
        print "Delta: %(T)s"%{"T":timeDelta}
        print solver2.model.prettyprint()

if __name__ == '__main__':
    newData = [[None, None, None,   1, None, 5,         None, 6, 8],
               [None, None, None,   None, None, None,   7, None, 1], 
               [0, None, 1,         None, None, None,   None, 3, None], 
               [None, None, 7,      None, 2, 6,         None, None, None],
               [5, None, None,      None, None, None,   None, None, 3],
               [None, None, None,       8, 7, None,         4, None, None],
               [None, 3, None,      None, None, None,   8, None, 5],
               [1, None, 5,         None, None, None,   None, None, None],
               [7, 0, None,         4, None, 1,         None, None, None]]
    newData1 = [[1, None, None,     None, None, None,   5, 6, 0],
               [4, 0, 2,            None, 5, 6,         1, None, 8], 
               [None, 5, 6,         1, None, 0,         2, 4, None], 
               [None, None, 0,      6, 4, None,         8, None, 1],
               [None, 6, 4,         None, 1, None,      None, None, None],
               [2, 1, 8,            None, 3, 5,         6,  None, 4],
               [None, 4, None,      5, None, None,      None, 1, 6],
               [0, None, 5,         None, 6, 1,         4, None, 2],
               [6, 2, 1,            None, None, None,   3, None, 5]]
    newData2 = [[None, None, 6,     None, None, None,   None, None, 4],
               [None, None, None,   8, 6, None,         7, 3, None], 
               [None, 4, None,      3, 5, None,         None, None, 2], 
               [1, 7, None,         4, None, None,      6, None, None],
               [None, 0, None,      None, None, None,   None, 8, None],
               [None, None, 8,      None, None, 6,      None,  1, 7],
               [2, None, None,      None, 8, 1,         None, 4, None],
               [None, 6, 7,         None, 4, 3,         None, None, None],
               [8, None, None,      None, None, None,   3, None, None]]
    test(newData)
    print ">>>"
    test(newData1)
    print ">>><<<"
    test(newData2)
    print ">>><<<>>>"
