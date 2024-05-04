A python translation of Anthay's C++ code. Find that here, and thank them because they did a lot more research than I did: https://github.com/anthay/ELIZA

## Requirements:
Built-ins are the only thing you need. Tested on python 3.7.

## Modules:
   - elizalogic       
     - The structures within elizalogic.py organize the rules that ELIZA uses to generate responses.
       - RuleBase: 
       - Script: Structure used to store the rules and memories used to generate responses.
       - RuleKeyword: A structure used to store a keyword rule. 
       - RuleMemory: A structure used to store prepared context based responses for use in the future.
       - Transform: A component of decomposition and reassembly.
       - Tracer: An abstract class used to build a history of movements through ELIZA's logic.
       - PreTracer: A tracer that specifies tracing before processing.
       - NullTracer: A tracer that indicates no tracing is done.
       - StringTracer: A tracer that tracks standard eliza response logic.
   - elizascript      
     - The classes within elizascript.py are designed to interpret a script comprised of the structures in elizalogic.py, 
     - from a plain text file. A tokenizer is used to identify symbols and segment text within the input stream.
       - Token: The tokenizer builds a list of these from a script.
       - Tokenizer: The tokenizer class, makes tokens.
       - StringIOWithPeek: As the name suggests, and we didn't necessarily need, this StringIO extension has peek().
       - ElizaScriptReader: Main script reader class.
   - elizaencoding        
     - Methods relating to the filtering of input outside of the original accepted character set, and hashing functions used to determine 'randomness' in eliza's responses.
   - eliza           
     - The main eliza class. Eliza takes a processed script, and generates responses based on the rules stored in it.
   - elizautil            
     - Various string processing utilities that ELIZA needs to generate it's responses.
   - elizatest     
     - TestInList
     - TestToInt
     - TestMadMatch
     - TestScriptReader
     - TestReassable
     - TestHashFunc
     - TestBCDFilter
     - TestEliza
     
   - elizaconstant 
     - The type definititions and constants used with ELIZA
       - TagMap
       - RuleMap
     
## Resources:
    + [DOCTOR_1966_01_CACM.py](DOCTOR_1966_01_CACM.py) - The original doctor script.
    + eliza_test_conversations.py
        - [cacm_1966_conversation.py](cacm_1966_conversation.py) - For testing purposes.
        - [cacm_1966_01_DOCTOR_TEST.py](cacm_1966_01_DOCTOR_TEST.py) - Comment stripped original script for testing purposes.

## Preview
![img.png](img.png)

