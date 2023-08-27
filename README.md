
# Python-Code-Dryrunner

Writing the dry run of a code manually is a tedious task especially for beginners in programming .<br> This project gives a dry run of the python code entered by user to analyse the changes occuring with the execution of each line. <br><br>

1. Ace editor is integrated into the frontend for taking user input.<br>
2. The frontend uses Fetch API to send the code entered to the backend and receive back the execution trace.<br>
3. Backend uses the Django framework and executes the python program under supervision of the standard python debugger module(bdb) .<br>
4. Program’s runtime state at every executed line is recorded and a JSON execution trace is sent back , which the frontend renders as the dry run.<br>

## Frontend :
Frontend Files <br>
1.index.html <br>
2.style.css<br>
3.front.js  - Sends the user input to backend and receives output trace .<br>
4.visualize.js - Renders the trace as the dry run<br>


## Backend: 
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

Lets look at how the execution trace is produced. Following is the code of exec_script_str in  DSLogger class of logger.py : <br><br>

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

<br><br>

DSLogger is a derived class of bdb.Bdb , which is the standard python debugger module  .<br> The self.run method is inherited from bdb.Bdb and it executes the contents of script.str.<br>The Bdb debugger has methods user_call , user_return ,  user_exception and user_line which are inherited in DSLogger class. <br><br>

As the user's pgrogram is running , bdb will pause execution at every function call , return , exception and single-line step. It transfers control to the respective handler methds . Since these methods are overridden in DSLogger , we can control how to interpret every line.<br><br>
## Exection Trace Format

The execution point of a single line which represents the state of computer's(abstract) memory notes the following details:<br>
1.ordered_globals - List of global variables in the order the frontend should visualize them. <br>
2.stdout - Any output to print in console. <br>
3.func_name - The function inside which the current line is executing . <br>
4.stack_to_render - The current memory stack . Helps in rendering recursive functions .<br>
5.globals- All the global variables . Helps in checking if a new variable is declared .<br>
6.heap- Used for handling dynamic memory allocated <br>
7.line - The line number about to execute .<br>
8.event -  Can be a function call , function return , an exception or a single line statement(most common)<br>

<br>








  
 
 


https://github.com/dsgreen2/Python-Code-Dryrunner/assets/106010465/e06ac207-f289-400e-9837-3c90ca0dab2b

