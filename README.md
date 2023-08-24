
# Python-Code-Dryrunner
Get a step by step dryrun of your python code.
Writing the dry run of a code manually is a tedious task especially for beginners in programming .<br> This project gives a dry run of the python code entered by user to analyse the changes occuring with the execution of each line. <br><br>

1. Ace editor is integrated into the frontend for taking user input.
<br>2. The frontend uses Fetch API to send the code entered to the backend and receive back the execution trace.
<br>3. Backend uses the Django framework and executes the python program under supervision of the standard python debugger module(bdb) .
<br>4. Program’s runtime state at every executed line is recorded and a JSON execution trace is sent back , which the frontend renders as the dry run.<br>

Frontend Files : index.html <br>style.css<br>front.js <br>visualize.js<br>

front.js sends the user input to backend and receives output trace .<br>
visualize.js renders the trace as the dry run<br>


Backend: <br>
1. views.py - Receives the data from frontend . Sends it to logger.py. Sends the data received from logger.py back to frontend.<br>
2. logger.py - Runs the python program under bdb debugger module and produces output trace. Calls encoder.py to encode data structure.<br>
3. encoder.py - Adds data structure created / updated in the trace.<br>

Backend Control Flow :<br>
The main entry point is the following function in logger.py:<br><br>

 def exec_script_str(script_str,raw_input_lst_json,finalizer)<br><br>
 1. script_str contains the entire string contents of the Python program for backend to execute.<br>
 2. finalizer is the function to call after the backend has executed trace.<br><br>

 A look at how the dryrun(request) function from views.py calls exec_script_str : <br><br>

ans=logger.exec_script_str(code_input,raw_input_json,finalizer_func)<br><br>

Lets look at how the execution trace is produced. Following is the code of exec_script_str in logger.py : <br><br>

def exec_script_str(script_str,raw_input_lst_json,finalizer):

```C++
    mylogger=DSLogger(finalizer)

    global input_string_queue
    input_string_queue=[]

    if raw_input_lst_json:
        input_string_queue=[str(e) for e in json.loads(raw_input_lst_json)]

    try:
        mylogger._runscript(script_str)
    
    except bdb.BdbQuit:
        pass

    finally:
       ans=mylogger.finalize()
       return ans

```









  
 
 


https://github.com/dsgreen2/Python-Code-Dryrunner/assets/106010465/e06ac207-f289-400e-9837-3c90ca0dab2b

