'''
Created on Apr 29, 2013

@author: francis.horsman:gmail.com
@important see todo!
TODO:   CALCULATE the avenues using an iterator using the original model
then we can dynamically create the sub-avenues depending on the events received,
rolling the model back at each avenue using the supplied callable.
'''

from newer.models.grid import grid
from newer.models.iModelNotifications import iModelNotifications
import collections

anAvenue = collections.namedtuple("Avenue", ["element", "possible", "depth", "model", "branches"])

class Hypothesiser(object):
    r"""@author: francis.horsman@gmail.com
    Hypothesis based on LogicError being yielded.
    """
    def __init__(self, model, pipelineSolver, abort, lock):
        self._model = None
        self._originalModel = model.serialize()
        self._listener = model._listeners["parent"]
        self._pipelineSolver = pipelineSolver
        self._abort = abort
        self._lock = lock
        self._init = False
        self._avenues = []
    def _createModel(self, data):
        model = grid.deserialize(data)
        model.addParentListener(self._listener)
        return model
    def stop(self):
        r"""
        @summary: Forcably stop hypothesising, clean up.
        """
        print "TODO: Stop hypothesiser..."
    def __call__(self, event):
        r"""
        @summary: An event has occurred, deal with it.
        @return: True = stop hypothesising (stop() will NOT be called).
        False - otherwise.
        """
        print "TODO: Implementing hypothesiser..."
        if event==iModelNotifications.UNSOLVABLE():
            #    No solution found - initial condition, also condition upon avenue.
            if self._init==False:
                self._init = True
                #    First time, calculate all possible avenues:
                self._avenues = Hypothesiser._calculateAvenues(self._originalModel, lambda: self._createModel(self._originalModel))
                #    Now execute the first avenue:
                return self._executeAvenue(self._avenues[0])
            else:
                #    No solution down this avenue...wind back one.
                return self._executeNextAvenue()
        elif event==iModelNotifications.LOGIC_ERROR():
            #    This avenue failed so the choice is WRONG, remove the possible
            #    from the parent's model, stop hypothesising and let the solver
            #    continue to solve again!
            rtn = self._wrongAvenue()
            #    Now reset the pipeline to force a resolve:
            self._pipelineSolver._resetPipeline()
            #    And we're good to go!
            return rtn
        else:
            print "!"
    def _executeAvenue(self, avenue=None):
        #    Find the first avenue:
        if avenue==None:
            for av in self._avenues:
                def getLeaf(ave):
                    if isinstance(ave.branches, list):
                        if len(ave.branches)>0:
                            return getLeaf(ave.branches[0])
                        else:
                            return
                    elif ave==-1:
                        return ave
                    elif ave==None:
                        pass
                avenue = getLeaf(av)
                if avenue!=None:
                    break
        if avenue==None:
            #    Terminate the Hypothesiser!
            self.stop()
            return True
        #    #    #    REPLACE BELOW    #    #    #
        if avenue.branches==None:
            #    Execute this node:
            uref = avenue.element
            value = avenue.possible
            newModel = avenue.model()
            with self._lock:
                #    Replace the model:
                self._pipelineSolver.model = newModel
                #    And set the value:
                el = newModel.findElement(uref.absRow, uref.absCol)
                el.setValue(value)
            #    Now reset the pipeline to force a resolve:
            self._pipelineSolver._resetPipeline()
            #    And we're good to go!
            avenue.branches = -1
        elif avenue.branches==-1:
            #    TODO: CURRENT: Avenue failed, create and try the sub-avenues:
            newModel = avenue.model()
            avenue.branches = Hypothesiser._calculateAvenues(newModel, lambda: self._createModel(self._originalModel))
        else:
            #    TODO: CURRENT: Implement this!
            #    execute the next sub-avenue.
            pass
        #    #    #    REPLACE ABOVE    #    #    #
        pass
    @staticmethod
    def _calculateAvenues(model, createModel, depth=0):
        #    FIXME: Make iterator.
        #    Create a flat tree of 'anAvenue's.
        avenues = []
        for el in model.iterUnknownElements():
            possibles = el.getPossibles()
            for possible in possibles:
                avenues.append(anAvenue(element=el.uRef,
                                        possible=possible,
                                        depth=depth,
                                        branches=None,
                                        model=createModel))
        return avenues
    def _XexecuteAvenue(self, avenues):
        avenue = avenues[0]
        #    Now execute this avenue, if it yields Unsolvable then create
        #    branches and proceed to the next one.
        pass
#         avenue.branches = copy.deepcopy(avenues[1:])
#         model = avenue.model()
#         for i in avenue.branches:
#             i.model = lambda: self._createModel(model)
    def _XnextAvenue(self):
        #    Check the next avenue is still valid, if so return it, otherwise
        #    get the next avenue!
        avenue = None
        while len(self._avenues)>0:
            avenue = self._avenues.pop(0)
            #    Check possible is still a possible for el!
            uref = avenue.element.uRef()
            self._model.findElement(uref.absRow, uref.absCol)
        return avenue
    def _XexecuteNextAvenue(self):
        self._model = self._createModel(self._originalModel)
        avenue = self._nextAvenue()
        if avenue==None:
            return True
        self._executeAvenue(self._avenues[0])





