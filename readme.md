


Recent Major Push: Mar 30, 2024

# Eliza, GDit
A (currently) intermediate python translation of anthay's C++ code, with a focus on equivalent feature representation and acceptance of scripts with original documentated formatting. 
It's destiny lies in the shape of GDscript.


## Modules:
   - elizalogic      - responsible for storing the structures associated with eliza, and the utilities needed to maintain those structures
   - elizascript     - responsible for loading eliza script based on the structures and logic managed by elizalogic
   - hollerith       - provides legacy utility related to the original eliza's input limitations
   - eliza           - responsible for interpreting the script and generating a response


## Progress:
   - elizascript core functionality passes all unit tests
   - hollerith passes all unit tests
   - elizalogic is partially complete and passes all dependent unit tests
   - eliza has been drafted, and is not complete.
   - match() is passing unit tests

## To-do:
   - other utility functions need unit tests before proceeding to interpretation logic.
   - eliza.py functionality needs to be moved to the appropriate module.
   - eliza needs unit tests made.
   - there are optimizations that can be made based on not being c++, without deviating from the goal
   - util.py is merged into the module __init__.py and can be removed
   - the old version of the tokenizer class can be removed (with caution)