# Python-Code-Dryrunner
Get a step by step dryrun of your python code.

Ace editor is integrated into the frontend for taking user input.
The frontend uses Fetch API to send the code entered to the backend and receive back the execution trace.
Backend uses the Django framework and executes the python program under supervision of the standard python debugger module(bdb) .
Program’s runtime state at every executed line is recorded and a JSON execution trace is sent back , which the frontend renders as the dry run.

Frontend Files : 
index.html
style.css
front.js
visualize.js
 
 
 
