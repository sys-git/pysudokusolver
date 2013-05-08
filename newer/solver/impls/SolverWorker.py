'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''

from Queue import Empty
from multiprocessing.synchronize import Event, RLock
from newer.models.LogicError import LogicError
from newer.models.grid import grid
from newer.models.iModelNotifications import iModelNotifications
from newer.solver.Abort import Abort
from newer.solver.AbortAck import AbortAck
from newer.solver.AbortError import AbortError
from newer.solver.Custom import Custom
from newer.solver.Logic import Logic
from newer.solver.PipelineSolver import PipelineSolver
from newer.solver.Solved import Solved
from newer.solver.UnSolveable import UnSolveable
from newer.solver.Update import Update
import itertools
import os
import threading
import traceback

class _Listener(object):
    def __init__(self, who, event, args):
        self.who = who
        self.event = event
        self.args = args

class SolverWorker(threading.Thread):
    tId = itertools.count()
    def __init__(self, tId, qRx, qTx, model):
        r"""
        tId = unique threadId - use in all comms with: qTx. 
        We can take as much time as we like here.
        @param qRx: Receive Abort, Update, 
        """
        self.tId = tId
        self._tId = SolverWorker.tId.next()
        self._qRx = qRx
        #    ATTENTION: qTx is the multiprocess boundary. Everything must be serialized outwards.
        self._qTx = qTx
        self._lock = RLock()
        self.hypothesising = None
        self._model = model
        self._model.addParentListener(self)
        self.abort = Event()
        self.abort.set()
        super(SolverWorker, self).__init__()
        self.setName("SolverWorker_%(P)s_%(T)s_%(T)s"%{"P":os.getpid(), "T":self.tId, "TT":self._tId})
        self.setDaemon(True)
        self.start()
    def getHypo(self):
        return self._hypothesising
    def setHypo(self, data):
        self._hypothesising = data
    hypothesising = property(getHypo, setHypo)
    def notification(self, who, event=None, args=None):
        self._sendNotification(who, event, args)
    def _sendNotification(self, who, event, args):
        msg = _Listener(who, event, args)
        try:
            self._qRx.put(msg)
        except Exception, _e:
            pass
    def _runSolver(self):
        t = threading.Thread(target=self._solve, args=[self._model, self._qRx, self.abort, self._lock])
        t.setName("SolverWorker_solver_%(P)s_%(T)s_%(T)s"%{"P":os.getpid(), "T":self.tId, "TT":self._tId})
        t.setDaemon(True)
        t.start()
        return t
    def run(self):
        self._runSolver()
        count = 0
        try:
            while self.abort.is_set():
                count += 1
                try:
                    msg = self._qRx.get(block=True, timeout=0.1)
                except EOFError:
                    break
                except Empty:
                    continue
                else:
                    with self._lock:
                        if isinstance(msg, _Listener):
                            if self._handleListenerEvent(msg):
                                break
                        elif isinstance(msg, LogicError):
                            if self._handlerLogicError(msg):
                                break
                        elif isinstance(msg, Update):
                            if self._handlerUpdateEvent(msg):
                                break
                        elif isinstance(msg, AbortError):
                            self.abort.clear()
                            break
                        elif isinstance(msg, Abort):
                            self.abort.clear()
                            break
                        else:
                            pass
        finally:
            if self.hypothesising!=None:
                self.hypothesising.stop()
                self.hypothesising = None
    def _handlerUpdateEvent(self, msg):
        if self.hypothesising!=None:
            self.hypothesising.stop()
            self.hypothesising = None
        self._model.update(msg.data)
    def _handleListenerEvent(self, msg):
        event = msg.event
        #    These are events that the outside world will be interested in:
        who = msg.who
        args = msg.args
        _map = {iModelNotifications.SOLVED():Solved, 
            iModelNotifications.UNSOLVABLE():UnSolveable,
            iModelNotifications.UPDATE():Update,
            iModelNotifications.CUSTOM():Custom,
            }
        if event in _map.keys():
            cls = _map[event]
            if event==iModelNotifications.CUSTOM():
                try:    self._qTx.put(cls(who, tId=self.tId, args=args))
                except Exception, _e:
                    pass
            elif who==grid.NAME:
                def send():
                    try:    self._qTx.put(cls(self._model, tId=self.tId, args=args))
                    except Exception, _e:
                        pass
                if event==iModelNotifications.SOLVED():
                    if self.hypothesising!=None:
                        self.hypothesising.stop()
                        self.hypothesising = None
                    send()
                    return True
                elif event==iModelNotifications.UNSOLVABLE():
                    if self.hypothesising!=None:
                        #    Trigger the next step:
                        rtn = self.hypothesising(event)
                    else:
                        #    Enter hypothesising mode:
#                         self.hypothesising = Hypothesiser(self._model, self._pipeline, self.abort, self._lock)
#                         rtn = self.hypothesising(event)
                        rtn = True
                    if rtn==True:
                        send()
                    return rtn
            else:
                if event==iModelNotifications.SOLVED():
                    event = iModelNotifications.UPDATE()
                    cls = _map[event]
                if event==iModelNotifications.UPDATE():
                    #    Get the relevant model data:
                    args = self._model._findFromUref(args)
                    try:    self._qTx.put(cls((who, args), tId=self.tId))
                    except: pass
        else:
            pass
    def _handlerLogicError(self, msg):
        if self.hypothesising!=None:
            return self.hypothesising(iModelNotifications.LOGIC_ERROR())
        try:    self._qTx.put(Logic(tId=self.tId))
        except Exception, _e:
            pass
        return True
    def _solve(self, model, qRx, abort, lock):
        #    Pipeline everything!
        self._pipeline = PipelineSolver(model, abort, lock)
        while self.abort.is_set():
            try:
                self._pipeline()
            except (Solved, UnSolveable), _e:
                break
            except AbortAck, _e:
                break
            except LogicError, e:
                try:
                    qRx.put(e)
                except Exception, _e:
                    traceback.print_exc()
                break
            except Exception, _e:
                print "SolverWorker.ERROR:\n%(T)s"%{"T":traceback.format_exc()}
                break
            pass

