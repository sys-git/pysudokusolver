'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''

from Queue import Empty
from multiprocessing.queues import Queue
from newer.solver.Abort import Abort
from newer.solver.AbortAck import AbortAck
from newer.solver.AbortError import AbortError
from newer.solver.AsyncSolverFactory import AsyncSolverFactory
from newer.solver.Custom import Custom
from newer.solver.Logic import Logic
from newer.solver.Solved import Solved
from newer.solver.SolverImplType import SolverImplType
from newer.solver.UnSolveable import UnSolveable
from newer.solver.Update import Update
import itertools
import threading
import traceback

class AsynchronousSolver(threading.Thread):
    tId = itertools.count()
    r"""
    @summary: Manages a suit of solver workers via queues, we could manage via a queue-like interface (PyRQ !).
    """
    def __init__(self, solvers, lock):
        self._solvers = solvers
        self._lock = lock
        self._q = Queue()
        self._qDistributor = Queue()
        self._queues = {}
        self._type = SolverImplType.THREADED
        super(AsynchronousSolver, self).__init__()
        self._go()
    def _go(self):
        model = self._solvers._getModel()
        for _ in xrange(self._solvers._count):
            q = Queue()
            tId = AsynchronousSolver.tId.next()
            asyncSolverImpl = AsyncSolverFactory(self._type, tId, self._qDistributor, q, model.clone())
            self._queues[tId] = (asyncSolverImpl, q)
            asyncSolverImpl.start()
        self.setName("AsynchronousSolver")
        self.setDaemon(True)
        self.start()
    def _terminate(self):
        self._informAbort()
        for context in self._queues.values():
            (thread, q) = context
            try:    q.put(Abort())
            except: pass
            try:    thread.terminate()
            except: pass
        self._queues = {}
    def get(self, *args, **kwargs):
        try:
            data = self._q.get(*args, **kwargs)
        except Empty:
            raise
        except Exception, e:
            print "AsynchronousSolver get: error:\n%(T)s"%{"T":traceback.format_exc()}
            raise e
        else:
            if isinstance(data, Exception):
                if not isinstance(data, (UnSolveable, Solved, AbortAck)) and isinstance(data, Exception):
                    print "AsynchronousSolver get resultant Exception:\n%(T)s\n"%{"T":traceback.format_exc()}
                else:
                    print "AsynchronousSolver get resultant data: '%(T)s'\n"%{"T":str(data)}
                raise data
            return data
    def run(self):
        print "AsynchronousSolver running..."
        e = None
        trace = ""
        try:
            self._work()
        except UnSolveable, e:
            print "AsynchronousSolver thread: Solving impossible!"
        except Solved, e:
            print "AsynchronousSolver thread: Solver solved!"
        except Exception, e:
            print "AsynchronousSolver thread exception:\n%(T)s\n"%{"T":traceback.format_exc()}
        try:    self._q.put(e)
        except Exception, _e:
            pass
        finally:
            try:    self._qDistributor.put(Abort())
            except Exception, _e:
                pass
            self._terminate()
            if trace!="":
                trace = "Error: '%(E)s"%{"E":trace}
            print "AsynchronousSolver thread finished\n'%(E)s'"%{"E":trace}
    def _work(self):
        r"""
        @summary: Funnel msgs to/from the solvers, updating our model as appropriate.
        """
        while self._solvers._abort.is_set():
            try:
                msg = self._qDistributor.get(block=True, timeout=1)
            except EOFError:
                break
            except Empty:
                continue
            else:
                if isinstance(msg, (Abort, AbortError)):
                    #    Tell all other instances to abort.
                    raise msg
                elif isinstance(msg, UnSolveable):
                    if not self._informUpdate(msg):
                        #    If this is the only solver, abort
                        raise msg
                elif isinstance(msg, Solved):
                    #    Tell all other instances to abort.
                    self._informUpdate(msg)
                    raise msg
                elif isinstance(msg, Update):
                    #    Fire the update to all other instances.
                    #    Update our model
                    self._informUpdate(msg)
                    self._q.put(msg)
                elif isinstance(msg, Custom):
                    try:
                        self._q.put(msg)
                    except Exception, _e:
                        pass
                elif isinstance(msg, Logic):
                    msg = ">>> >> > Logic inconsistancy < << <<<"
                    print msg
                    raise Exception(msg)
    def _informUpdate(self, msg):
        try:
            tId = msg.tId
        except:
            tId = None
        return self._inform(msg, tId)
    def _informAbort(self, msg=None):
        try:
            tId = msg.tId
        except:
            tId = None
        return self._inform(Abort(), tId)
    def _inform(self, msg, tId):
        threads = self._queues.keys()
        try:    threads.remove(tId)
        except: pass
        for context in threads:
            (_thread, q) = self._queues[context]
            try:    q.put(msg)
            except: pass
        return (len(threads)>0)

