'''
Created on 18 Mar 2013

@author: francis.horsman:gmail.com
'''
from multiprocessing.process import Process
from newer.solver.SolverImplType import SolverImplType
from newer.solver.impls.SolverWorker import SolverWorker
import threading

class AsyncSolverFactory(object):
    def __new__(self, type_, tId, qDistributor, q, model):
        if type_==SolverImplType.THREADED:
            thread = threading.Thread(target=SolverWorker, args=[tId, q, qDistributor, model])
            thread.setName("LoopingSolver_thread_%(I)s"%{"I":tId})
            thread.setDaemon(True)
        elif type_==SolverImplType.MULTIPROCESSOR:
            thread = Process(target=SolverWorker, args=[tId, q, qDistributor, model])
            thread.setName("LoopingSolver_process_%(I)s"%{"I":tId})
            thread.setDaemon(True)
        else:
            raise TypeError("Unknown SolverImplType: '%(T)s'."%{"T":type_})
        return thread
