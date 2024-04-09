


Recent Major Push: Mar 30, 2024

# Eliza, GDit
A python translation of anthay's C++ code, with a focus on equivalent feature representation and the acceptance of scripts with original documented formatting.


## Modules:
   - elizalogic      - responsible for storing the structures associated with eliza, and the utilities needed to maintain those structures
   - elizascript     - responsible for loading eliza script based on the structures and logic managed by elizalogic
   - hollerith       - provides legacy utility related to the original eliza's input limitations
   - eliza           - responsible for interpreting the script and generating a response


## Progress:
   - elizascript core functionality passes all unit tests
   - hollerith passes all unit tests
   - elizalogic passes all unit tests
   - eliza has partially completed.
   - eliza conversation unit test created, not passing
   - Main program routine created

## To-do:
   - Something is wrong in complex transforms