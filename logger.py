import io
import sys
import bdb
import re
import traceback 
import types
import dsencoder

CLASS_RE=re.compile('class\s+')

IGNORE_VARS=set(('__user_stdout__','__OPT_toplevel__','__builtins__','__name__','__exception__','__doc__','__package__'))

MAX_EXECUTED_LINES=1000

DEBUG=True

BREAKPOINT_STR="#break"

# list of allowed modules to be imported 
if type(__builtins__) is dict:
    BUILTIN_IMPORT = __builtins__['__import__']
else:
    assert type(__builtins__) is types.ModuleType
    BUILTIN_IMPORT=__builtins__.__import__

ALLOWED_STDLIB_MODULE_IMPORTS = ('math', 'random', 'time', 'datetime','functools', 'itertools', 'operator', 'string','collections', 're', 'json','heapq', 'bisect', 'copy', 'hashlib')
OTHER_STDLIB_WHITELIST = ('StringIO', 'io')

CUSTOM_MODULE_IMPORTS = ()


for m in ALLOWED_STDLIB_MODULE_IMPORTS + CUSTOM_MODULE_IMPORTS:
    __import__(m)


def __restricted_import__(*args):
    
    args = [e for e in args if type(e) is str]
    if args[0] in ALLOWED_STDLIB_MODULE_IMPORTS + CUSTOM_MODULE_IMPORTS + OTHER_STDLIB_WHITELIST:
        imported_mod = BUILTIN_IMPORT(*args)
        
        if args[0] in CUSTOM_MODULE_IMPORTS:
            setattr(imported_mod, 'setHTML', setHTML)
            setattr(imported_mod, 'setCSS', setCSS)
            setattr(imported_mod, 'setJS', setJS)
            
        
        for mod in ('os', 'sys', 'posix', 'gc'):
            if hasattr(imported_mod, mod):
                delattr(imported_mod, mod)
                
        return imported_mod
        
    else:
         raise ImportError('{0} not supported'.format(args[0]))


import random
random.seed(0)

input_string_queue=[]

def open_wrapper(*args):
    raise Exception('''Open() is not supported currently. ''')

def create_banned_builtins_wrapper(fn_name):
    def err_func(*args):
        raise Exception("'" + fn_name + "' is not supported currently.")
        
    return err_func

class RawInputException(Exception):
  pass

def raw_input_wrapper(prompt=''):

    if input_string_queue:
        input_str=input_string_queue.pop(0)
        sys.stdout.write(str(prompt))
        sys.stdout.write(input_str+"\n")
        return input_str

    raise RawInputException(str(prompt))

class MouseInputException(Exception):
    pass

def mouse_input_wrapper(prompt=''):
    if input_string_queue:
        return input_string_queue.pop(0)

    raise MouseInputException(prompt)

BANNED_BUILTINS = ['reload', 'open', 'compile','file', 'eval', 'exec', 'execfile','exit', 'quit', 'help','dir', 'globals', 'locals', 'vars']


def get_user_stdout(frame):
    my_user_stdout=frame.f_globals['__user_stdout__']

    return my_user_stdout.getvalue()




def get_user_globals(frame,at_global_scope=False):

    d=filter_var_dict(frame.f_globals)

    if '__return__' in d:
        del d['__return__']

    return d


def get_user_locals(frame):

    ret=filter_var_dict(frame.f_locals)

    f_name=frame.f_code.co_name

    if hasattr(frame,'f_valuestack'):
        if f_name.endswith('comp>'):
            l=[]
            for i in frame.f_valuestack:
                if type(i) in (list,set,dict):
                    l.append(i)
            for (i,e) in enumerate(l):
                ret['_tmp'+str(i+1)]=e
    
    return ret

def filter_var_dict(d):
    ret={}
    for (k,v) in d.items():
        if k not in IGNORE_VARS:
            ret[k]=v
    return ret



def visit_all_locally_reachable_function_objs(frame):
    for(k,v) in get_user_locals(frame).items():
        for e in visit_function_obj(v,set()):
            if e:
                assert type(e) in (types.FunctionType,types.MethodType)
                yield e

def visit_function_obj(v,ids_seen_set):
    v_id=id(v)

    if v_id in ids_seen_set:
        yield None
    else:
        ids_seen_set.add(v_id)
        typ=type(v)

        if typ in (types.FunctionType,types.MethodType):
            yield v
        
        elif typ in (list,tuple,set):
            for child in v:
                for child_res in visit_function_obj(child,ids_seen_set):
                    yield child_res
        
        elif typ==dict :
            contents_dict=v

            if contents_dict:
                for(key_child,val_child) in contents_dict.items():
                    for key_child_res in visit_function_obj(key_child,ids_seen_set):
                        yield key_child_res 
                    for val_child_res in visit_function_obj(val_child,ids_seen_set):
                        yield val_child_res
        
        yield None




class DSLogger(bdb.Bdb):

    def __init__(self,finalizer):

        bdb.Bdb.__init__(self)
        self.mainpyfile=''
        self.wait_for_mainpyfile=0

        self.trace=[]

        self.done=False

        self.wait_for_return_stack=None

        self.GAE_STDOUT = sys.stdout

        self.closures={}

        self.lambda_closures={}

        self.globally_defined_funcs=set()

        self.frame_ordered_ids={}
        self.cur_frame_id=1

        self.zombie_frames=[]

        self.parent_frames_set=set()

        self.all_globals_in_order=[]

        self.render_heap_primitives=None

        self.encoder=dsencoder.ObjectEncoder(self.render_heap_primitives)

        self.executed_script=None

        self.breakpoints=[]
        self.prev_lineno=-1

        self.final_func=finalizer

        self.ORIGINAL_STDERR=None

    def get_frame_id(self,cur_frame):
        return self.frame_ordered_ids[cur_frame]

   

    def get_parent_of_function(self,val):
         if val in self.closures:
            return self.get_frame_id(self.closures[val])
        
         elif  val in self.lambda_closures:    
            return self.get_frame_id(self.lambda_closures[val])
         else:
            return None

    
    def get_parent_frame(self,frame):

        for (func_object,parent_frame) in self.closures.items():

            if func_obj.__code__==frame.f_code:
                all_matched=True

                for k in frame.f_locals:

                    if k in frame.f_code.co_varnames:
                        continue
                    
                    if k !='__return__' and k in parent_frame.f_locals:
                        if parent_frame.f_locals[k] !=frame.f_locals[k]:
                            all_matched=False
                            break
                
                if all_matched:
                    return parent_frame
        

        for (lambda_code_obj,parent_frame) in self.lambda_closures.items():
            if lambda_code_obj==frame.f_code:
                return parent_frame
        
        return None
    

    def forget(self):

        self.lineno=None
        self.stack=[]
        self.curindex=0
        self.curframe=None

    def setup(self,f,t):
        self.forget()
        self.stack,self.curindex=self.get_stack(f,t)
        self.curframe=self.stack[self.curindex][0]

    
    def get_stack_code_IDs(self):
        return [id(e[0].f_code) for e in self.stack]





    def user_call(self,frame,argument_list):

        if self.done: return

        if self.wait_for_mainpyfile: return 

        if self.stop_here(frame):

            try:
                del frame.f_locals['__return__']
            except KeyError:
                pass

            self.interaction(frame,None,'call')

 
    
    def user_line(self,frame):

        if self.done: return

        if self.wait_for_mainpyfile:
            if(self.canonic(frame.f_code.co_filename)!="<string>" or frame.f_lineno<=0):
                return
            self.wait_for_mainpyfile=0
        self.interaction(frame,None,'step_line')

    def user_return(self,frame,return_value):

        if self.done: return

        frame.f_locals['__return__']=return_value
        self.interaction(frame,None,'return')

    def user_exception(self,frame,exc_info):

        if self.done: return

        exc_type,exc_value,exc_traceback=exc_info

        frame.f_locals['__exception__']=exc_type,exc_value

        if type(exc_type)==type(''):
            exc_type_name=exc_type
        
        else: 
            exc_type_name=exc_type.__name__
        
        if exc_type_name=='RawInputException':
            raw_input_arg=str(exc_value.args[0])
            self.trace.append(dict(event='raw_input',prompt=raw_input_arg))
            self.done=True

        elif exc_type_name=='MouseInputException':
            mouse_input_arg=str(exc_value.args[0])
            self.trace.append(dict(event='mouse_input',prompt=mouse_input_arg))
            self.done=True
        
        else:
            self.interaction(frame,exc_traceback,'exception')

    def lookup_zombie_frame_by_id(self,frame_id):

        for e in self.zombie_frames:
            if self.get_frame_id(e)==frame_id:
                return e
        assert False


    def interaction(self,frame,traceback,event_type):

        self.setup(frame,traceback)
        tos=self.stack[self.curindex]
        top_frame = tos[0]
        lineno = tos[1]


        if self.canonic(top_frame.f_code.co_filename) != '<string>':
          return

        if top_frame.f_code.co_name == '__new__':
          return
        
        if top_frame.f_code.co_name == '__repr__':
          return

        if '__OPT_toplevel__' not in top_frame.f_globals:
          return

        
        if self.wait_for_return_stack:

            if event_type=='return' and (self.wait_for_return_stack==self.get_stack_code_IDs()):
                self.wait_for_return_stack=None
            
            return
        else:

            if event_type=="call":
                func_line=self.executed_script_lines[(top_frame.f_code.co_firstlineno)-1]

                if CLASS_RE.match(func_line.lstrip()):
                    self.wait_for_return_stack=self.get_stack_code_IDs()
                    return

        self.encoder.reset_heap()

        if event_type=="call":

            self.frame_ordered_ids[top_frame]=self.cur_frame_id
            self.cur_frame_id+=1
        
        cur_stack_frames=[e[0] for e in self.stack[:self.curindex+1]]
        
        zombie_frames_to_render = [e for e in self.zombie_frames if e not in cur_stack_frames]

        encoded_stack_locals=[]
        
        def create_encoded_stack_entry(cur_frame):
            ret={}
            parent_frame_id_list=[]
            f=cur_frame
            
            while True:
                
                p=self.get_parent_frame(f)
                
                if p:
                    pid=self.get_frame_id(p)
                    assert pid
                    parent_frame_id_list.append(pid)
                    f=p
                
                else:
                    break
                
            cur_name=cur_frame.f_code.co_name
            
            if cur_name=='':
                cur_name='unnamed function'
                
            if cur_name=='<lambda>':
                cur_name+=dsencoder.create_lambda_line_number(cur_frame.f_code,self.encoder.line_to_lambda_code)
            
            encoded_locals={}
            
            for(k,v) in get_user_locals(cur_frame).items():
                is_in_parent_frame=False
                
                for pid in parent_frame_id_list:
                    
                    parent_frame=self.lookup_zombie_frame_by_id(pid) # get a list of all the frames 
                    
                    if k in parent_frame.f_locals:
                        
                        if k!='__return__':
                            
                            if parent_frame.f_locals[k]==v:
                                is_in_parent_frame=True
                                
                if is_in_parent_frame and k not in cur_frame.f_code.co_varnames:
                    continue
                
                if k=='__module__':
                    continue
                
                encoded_val=self.encoder.encode(v,self.get_parent_of_function)

                encoded_locals[k]=encoded_val
                
            ordered_varnames=[]
            
            for  e  in cur_frame.f_code.co_varnames:
                if e in encoded_locals:
                    ordered_varnames.append(e)
                    
            for e in sorted(encoded_locals.keys()):
                if e!='__return__' and e not in ordered_varnames:
                    ordered_varnames.append(e)
                    
            if '__return__' in encoded_locals:
                ordered_varnames.append('__return__')
                
            if '__locals__' in encoded_locals:
                ordered_varnames.remove('__locals__')
                local=encoded_locals.pop('__locals__')      
                
                if encoded_locals.get('__return__',True) is None:
                    encoded_locals['__return__']=local
                    
            
            assert len(ordered_varnames)==len(encoded_locals)
            for e in ordered_varnames:
                assert e in encoded_locals
                
            return dict(func_name=cur_name,
            is_parent=(cur_frame in self.parent_frames_set),
            frame_id=self.get_frame_id(cur_frame),
            parent_frame_id_list=parent_frame_id_list,
            encoded_locals=encoded_locals,
            ordered_varnames=ordered_varnames)          
            
        i=self.curindex
        
        if i>1:
            
            for v in visit_all_locally_reachable_function_objs(top_frame):
                if (v not in self.closures and v not in self.globally_defined_funcs):
                    chosen_parent_frame=None
                    
                    for (my_frame,my_lineno) in reversed(self.stack):
                        if chosen_parent_frame:
                            break
                        
                        for frame_const in my_frame.f_code.co_consts:
                            if frame_const is v.__code__:
                                chosen_parent_frame=my_frame
                                break

                    if chosen_parent_frame in self.frame_ordered_ids:
                        self.closures[v]=chosen_parent_frame
                        self.parent_frames_set.add(chosen_parent_frame)
                        if not chosen_parent_frame in self.zombie_frames:
                            self.zombie_frames.append(chosen_parent_frame)

            else:
                if top_frame.f_code.co_consts:
                    for e in top_frame.f_code.co_consts:
                        if type(e)==types.CodeType and e.co_name=='<lambda>':
                            self.lambda_closures[e]=top_frame
                            self.parent_frames_set.add(top_frame)
                            if not top_frame in self.zombie_frames:
                                self.zombie_frames.append(top_frame)

        
        else:
            for (k,v) in get_user_globals(top_frame).items():
                if (type(v) in (types.FunctionType,types.MethodType) and v not in self.closures):
                    self.globally_defined_funcs.add(v)

        while True:
            cur_frame=self.stack[i][0]
            cur_name=cur_frame.f_code.co_name
            if cur_name=='<module>':
                break

            if cur_frame in self.frame_ordered_ids:
                encoded_stack_locals.append(create_encoded_stack_entry(cur_frame))
            i-=1

        zombie_encoded_stack_locals=[create_encoded_stack_entry(e) for e in zombie_frames_to_render]


        encoded_globals={}

        for (k,v) in get_user_globals(tos[0],at_global_scope=(self.curindex<=1)).items():
            encoded_val=self.encoder.encode(v,self.get_parent_of_function)
            encoded_globals[k]=encoded_val

            if k not in self.all_globals_in_order:
                self.all_globals_in_order.append(k)
        
        ordered_globals=[e for e in self.all_globals_in_order if e in encoded_globals]
        assert len(ordered_globals)==len(encoded_globals)

        stack_to_render=[]

        if encoded_stack_locals:
            for e in encoded_stack_locals:
                e['is_zombie']=False
                e['is_highlighted']=False
                stack_to_render.append(e)

            stack_to_render[0]['is_highlighted']=True
        
        for e in zombie_encoded_stack_locals:
            e['is_zombie']=True
            e['is_highlighted']=False

            stack_to_render.append(e)
        
        stack_to_render.sort(key=lambda e:e['frame_id'])

        for e in stack_to_render:
            hash_str=e['func_name']

            hash_str+='_f'+str(e['frame_id'])

            if e['is_parent']:
                hash_str+='_p'
            
            if e['is_zombie']:
                hash_str+='_z'

            e['unique_hash']=hash_str
        

        trace_entry=dict(line=lineno,
                         event=event_type,
                         func_name=tos[0].f_code.co_name,
                         globals=encoded_globals,
                         ordered_globals=ordered_globals,
                         stack_to_render=stack_to_render,
                         heap=self.encoder.get_heap(),
                         stdout=get_user_stdout(tos[0]))
        
        if event_type=='exception':
            exc=frame.f_locals['__exception__']
            trace_entry['exception_msg']=exc[0].__name__+': '+str(exc[1])

        append_to_trace=True

        if self.breakpoints:
            if not ((lineno in self.breakpoints) or (self.prev_lineno in self.breakpoints)):
                append_to_trace=False

            if event_type=='exception':
                append_to_trace=True

        self.prev_lineno=lineno

        if append_to_trace:
            self.trace.append(trace_entry)

        
        if len(self.trace)>=MAX_EXECUTED_LINES:
            self.trace.append(dict(event='instruction limit reached'))
            self.force_terminate()
        
        self.forget()

        

    def _runscript(self,script_str,custom_globals=None):

        self.executed_script=script_str

        self.executed_script_lines = self.executed_script.splitlines()

        for (i, line) in enumerate(self.executed_script_lines):
            line_no = i + 1
            if line.endswith('#break'):
                self.breakpoints.append(line_no)

        self.wait_for_mainpyfile=1

        user_builtins={}
        if type(__builtins__) is dict:
            builtin_items=__builtins__.items()

        else:
            assert type(__builtins__) is types.ModuleType
            builtin_items=[]
            for k in dir(__builtins__):
                builtin_items.append((k,getattr(__builtins__,k)))

        for (k,v) in builtin_items:

            if k in BANNED_BUILTINS:
                user_builtins[k]=create_banned_builtins_wrapper(k)
            
            elif k == '__import__':
                user_builtins[k] = __restricted_import__
            else:
                if k=='raw_input':
                    user_builtins[k] = raw_input_wrapper
                elif k=='input':
                    user_builtins[k]=raw_input_wrapper
                else :
                    user_builtins[k]=v
        
        user_builtins['mouse_input']=mouse_input_wrapper

        user_stdout=io.StringIO()

        sys.stdout=user_stdout

        self.ORIGINAL_STDERR=sys.stderr

        user_globals={"__name__":"__main__",
                      "__builtins__":user_builtins,
                      "__user_stdout__":user_stdout,
                      "__OPT_toplevel__":True
                      }

        if custom_globals:
            user_globals.update(custom_globals)
        
        try:

            self.run(script_str,user_globals,user_globals)

        except SystemExit:
            raise bdb.BdbQuit
        
        except:
            if DEBUG:
                traceback.print_exc()

            trace_entry=dict(event='uncaught_exception')

            (exc_type,exc_val,exc_tb)=sys.exc_info()

            if hasattr(exc_val,'lineno'):
                trace_entry['line']=exc_val.lineno
            
            if hasattr(exc_val,'offset'):
                trace_entry['offset']=exc_val.offset

            trace_entry['exception_msg']=type(exc_val).__name__+": "+str(exc_val)

            already_caught=False

            for e in self.trace:
                if e['event']=='exception':
                    already_caught=True
                    break
            
            if not already_caught:
                if not self.done:
                    self.trace.append(trace_entry)
            
            raise bdb.BdbQuit
        
    def force_terminate(self):
        raise bdb.BdbQuit

    def finalize(self):

        sys.stdout=self.GAE_STDOUT
        sys.stderr=self.ORIGINAL_STDERR

        assert len(self.trace)<=(MAX_EXECUTED_LINES+1)

        res=self.trace
        
        if len(res)>=2 and res[-2]['event']=='exception' and res[-1]['event']=='return' and res[-1]['func_name']=='<module>':
            res.pop()

        self.trace=res

        return self.final_func(self.executed_script,self.trace)
    
import json




def exec_script_str(script_str,raw_input_lst_json,finalizer):

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


#def exec_script_str_local(script_str,raw_input_lst_json):

 
 #   mylogger=DSLogger()

  
  #  global input_string_queue
   # input_string_queue=[]

    #if raw_input_lst_json:
     #   input_string_queue=[str(e) for e in json.loads(raw_input_lst_json)]
        
    #try:
     #   mylogger._runscript(script_str)
    
    #except bdb.BdbQuit:
     #   pass
    #finally:
     #   return mylogger.finalize()
    


