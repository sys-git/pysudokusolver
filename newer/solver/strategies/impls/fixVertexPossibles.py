'''
Created on Apr 9, 2013

@author: francis.horsman:gmail.com
'''

from newer.models.aRow import aRow

class fixVertexPossibles(object):
    r"""@author: francis.horsman@gmail.com
    """
    def _rolCol(self, model, attrNameGetter, attrNameSetter, otherVertexName):
        updated = [0]
        class listener(object):
            def notification(self, who, *args, **kwargs):
                updated[0] += 1
        myListener = listener()
        model.addListener(myListener)
        try:
            while updated[0]>0:
                self._checkAbort()
                updated[0] = 0
                #    Check each ROW and update the POSSIBLES/VALUES.
                for vertex in getattr(model, attrNameGetter):
                    self._checkAbort()
                    vertex = aRow(vertex)
                    known = vertex.knowns()
                    unknown = vertex.unknown()
                    unknowns = vertex.unknowns()
                    if len(unknowns)==1:
                        #    We have 1 unknown so fill it in!
                        (_element, otherVertex) = unknowns[0]
                        missingValue = list(unknown)[0]
                        vertex[otherVertex].value = missingValue
                    #    Tell the other elements that each value is not a possible.
                    if len(list(known))>0:
                        for element in vertex:
                            element.setPossibles(element.getPossibles()-known)
        finally:
            model.removeListener(myListener)
