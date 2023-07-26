
https://github.com/dsgreen2/Python-Code-Dryrunner/assets/106010465/43256a2c-c60d-4ea4-8578-70807ace5408
# Python-Code-Dryrunner
Get a step by step dryrun of your python code.

Ace editor is integrated into the frontend for taking user input.
<br>The frontend uses Fetch API to send the code entered to the backend and receive back the execution trace.
<br>Backend uses the Django framework and executes the python program under supervision of the standard python debugger module(bdb) .
<br>Program’s runtime state at every executed line is recorded and a JSON execution trace is sent back , which the frontend renders as the dry run.<br>

Frontend Files : index.html <br>style.css<br>front.js <br>visualize.js<br>

front.js sends the user input to backend and receives output trace .<br>
visualize.js renders the trace as the dry run<br>


Backend: <br>
views.py - Receives the data from frontend . Sends it to logger.py. Sends the data received from logger.py back to frontend.<br>
logger.py - Runs the python program under bdb debugger module and produces output trace. Calls encoder.py to encode data structure.<br>
encoder.py - Adds data structure created / updated in the trace.<br>
 
 
 


https://github.com/dsgreen2/Python-Code-Dryrunner/assets/106010465/e06ac207-f289-400e-9837-3c90ca0dab2b

