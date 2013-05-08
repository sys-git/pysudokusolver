pysudokusolver
==============

2-dimensional Sudoku solver
This is a greenfield piece of work without looking at any previous solutions presented anywhere else, just from my brain.
The only thing taken from elsewhere iare the XWing and YWing strategies - as referenced in those files.

Not saying this will be elegant/efficient for a first draft but I want it to at least scale via multi-processing and multi-threading, then we can look at a port to Celery/Picloud for some seriously monster sized sudoku solving.
The model is coupled to the solver, not good.
The serialization is slow!
TODO: Use a database to store the grid elements and their value arrays.
At the moment, the Update, Solved and Unsolvable exceptions/Messages that cross the multiprocessing boundary require a serialization of the model, this is slow and inefficient!

Any comments about the UI (which is purely to aid debugging - not designed to be written properly, asynchronous, etc), setup.py, non-optimisation, lack of configuration/documentation, in fact-anything will be sent to /dev/null.
To add strategies which use the model: grid.py, place these in newer/solver/strategies/impls with same filename as classname (upper-case first char of filename).
