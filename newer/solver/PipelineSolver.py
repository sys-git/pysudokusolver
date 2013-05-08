'''
Created on 5 Apr 2013

@author: francis.horsman:gmail.com
'''

from multiprocessing.synchronize import Event
from newer.models import LogicError
from newer.models.grid import grid
from newer.models.iModelNotifications import iModelNotifications
from newer.solver.AbortAck import AbortAck
from newer.solver.Solved import Solved
from newer.solver.UnSolveable import UnSolveable
from newer.solver.strategies.StrategiesFactory import StrategiesFactory
import time
import traceback

class PipelineSolver(object):
    def __init__(self, model, abort, lock):
        self.model = model
        self.abort = abort
        self.lock = lock
        self.event = Event()
        self.event.clear()
        self.args = []
        self.unsolvable = False
        self.solved = False
        model.addParentListener(self)
        self._strategies = StrategiesFactory(model, self._checkAbort, lambda: self.solved, lambda: self.unsolvable)
        self._resetPipeline()
    def notification(self, who, event=None, args=None):
        if who==grid.NAME:
            if event in [iModelNotifications.ALL(), iModelNotifications.SOLVED(), iModelNotifications.UNSOLVABLE]:
                self.args = []
            if event==iModelNotifications.SOLVED():
                self.solved = True
            if event==iModelNotifications.UNSOLVABLE():
                self.unsolvable = True
        if event==iModelNotifications.CUSTOM():
            return
        self.args.append((event, args))
    def __call__(self):
        try:
            if self.unsolvable:
                raise UnSolveable(self.model)
            if self.solved or self.model.solved:
                raise Solved(self.model)
            eventCount = self._eventCount()
            if len(self.pipeline)>0 or eventCount>0:
                self._executePipeline(eventCount)
            else:
                print "out of rules!"
                raise UnSolveable(self.model)
        except (Solved, UnSolveable, AbortAck), e:
            if isinstance(e, Solved):
                self.solved = True
                self.model.solved = True
            elif isinstance(e, UnSolveable):
                self.unsolvable = True
                self.model.unsolvable = True
            self.args = []
            self.pipeline = []
            raise
    def _resetPipeline(self):
        self.pipeline = self._strategies()
    def _eventCount(self):
        return len(self.args)
    def _executePipeline(self, numEvents):
        try:
            (event, args) = self.args.pop(0)
            lenArgs = len(self.args)
        except IndexError, _e:
            pipeline = self.pipeline.pop(0)
            with self.lock:
                name = pipeline.name
                diff = pipeline.difficulty
                print "Executing: %s"%name
                delta = None
                timeStart = time.time()
                try:
                    self.model.customEvent(args={"strategy":name, "difficulty":diff, "timeStart":timeStart})
                    pipeline(self.model)
                except LogicError, _e:
                    raise
                except Exception, _e:
                    print "Error executing pipeline: '%s':\n%s"%(name, traceback.format_exc())
                    raise
                else:
                    delta = self._eventCount()-numEvents
                    print "pipeline: '%s' yielded '%d' modifications!"%(name, delta)
                finally:
                    if delta==None:
                        delta = self._eventCount()-numEvents
                    timeEnd = time.time()
                    self.model.customEvent(args={"strategy":name, "difficulty":diff, "timeStart":timeStart, "timeEnd":timeEnd, "yield":delta})
                self._checkAbort()
                self._checkValidation()
        else:
            #    Deal with the data that has changed.
            with self.lock:
                self._executeArgs(event, args, lenArgs)
        if self._eventCount()>numEvents:
            self._resetPipeline()
            self.args = []
    def _executeArgs(self, event, args, lenArgsFromEvent):
        #    An event has occurred, somehow, do we need to rework?
        #    For now, simply reset the pipeline.
        #    Ideally we would want to work based on events that have occurred.
        print "EXECUTE ARGS: '%(E)s' - '%(A)s'."%{"A":args, "E":event}
        self._resetPipeline()
        self.args = []
    def _checkValidation(self):
        self.model.checkValidation()
    @staticmethod
    def _addListeners(model, listener):
        model.addListener(listener)
    @staticmethod
    def _removeListeners(model, listener):
        model.removeListener(listener)
    def _checkAbort(self):
        if not self.abort.is_set() or self.unsolvable or self.solved:
            raise AbortAck()
