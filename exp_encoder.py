FLOAT_PRECISION=4

from collections import defaultdict
import re,types
import sys
import math
typeRE=re.compile("<type '(.*)'>")
classRE=re.compile("<class '(.*)'>")

import inspect

long=int
unicode=str

def get_name(obj):
    return obj.__name__ if hasattr(obj, '__name__') else get_name(type(obj))


PRIMITIVE_TYPES=(int,long,float,str,unicode,bool,type(None))

def encode_primitive(dat):
    t=type(dat)
    if t is float:
        if math.isinf(dat):
            if dat>0:
                return ['SPECIAL_FLOAT','Infinity']
            else:
                return ['SPECIAL_FLOAT','-Infinity']
        
        elif math.isnan(dat):
            return ['SPECIAL_FLOAT','NaN']
        
        else:
            if dat==int(dat):
                return ['SPECIAL_FLOAT','%.1f'%dat]
            else:
                return round(dat,FLOAT_PRECISION)
    
    else:
        return dat

def create_lambda_line_number(codeobj,line_to_lambda_code):

    try:
        lambda_lineno=codeobj.co_firstlineno
        lst=line_to_lambda_code[lambda_lineno]
        ind=lst.index(codeobj)

        lineno_str=str(lambda_lineno)
        return ' <line '+lineno_str+'>'
    
    except:
        return ''
    

class ObjectEncoder:

    def __init__(self,render_heap_primitives):

        self.encoded_heap_objects={}

        self.render_heap_primitives=render_heap_primitives

        self.id_to_small_IDs={}
        self.cur_small_ID=1

        self.line_to_lambda_code=defaultdict(list)
            
    def get_heap(self):
        return self.encoded_heap_objects
    
    def reset_heap(self):

        self.encoded_heap_objects={}

    def set_function_parent_frame_ID(self,ref_obj,enclosing_frame_id):
        assert ref_obj[0]=='REF'
        func_obj=self.encoded_heap_objects[ref_obj[1]]
        assert func_obj[0]=='FUNCTION'
        func_obj[-1]=enclosing_frame_id

    def encode(self,dat,get_parent):

        if not self.render_heap_primitives and type(dat) in PRIMITIVE_TYPES:
            return encode_primitive(dat)
        
        else:
            my_id=id(dat)

            try:
                my_small_id=self.id_to_small_IDs[my_id]

            except KeyError:
                my_small_id=self.cur_small_ID
                self.id_to_small_IDs[my_id]=self.cur_small_ID
                self.cur_small_ID+=1

            del my_id

            ret=['REF',my_small_id]

            if my_small_id in self.encoded_heap_objects:
                return ret
            
            new_obj=[]
            self.encoded_heap_objects[my_small_id]=new_obj

            typ=type(dat)

            if typ==list:
                new_obj.append('LIST')
                for e in dat:
                    new_obj.append(self.encode(e,get_parent))

            elif typ==tuple:
                new_obj.append('TUPLE')
                for e in dat:
                    new_obj.append(self.encode(e,get_parent))
            
            elif typ==set:
                new_obj.append('SET')
                for e in dat:
                    new_obj.append(self.encode(e,get_parent))
            
            elif typ==dict:
                new_obj.append('DICT')
                for (k,v) in dat.items():
                    if k not in ('__module__','__return__','__locals__'):
                        new_obj.append([self.encode(k,get_parent),self.encode(v,get_parent)])

            elif typ in (types.FunctionType,types.MethodType):
                argspec=inspect.getfullargspec(dat)

                printed_args=[e for e in argspec.args]
                if argspec.varargs:
                    printed_args.append('*'+argspec.varargs)

                if argspec.varkw:
                    printed_args.append('**'+argspec.varkw)
                if argspec.kwonlyargs:
                    printed_args.extend(argspec.kwonlyargs)
                
             
                func_name=get_name(dat)

                pretty_name=func_name

                try:
                    pretty_name += '(' + ', '.join(printed_args) + ')'
                except TypeError:
                    pass

                if func_name=='<lambda>':
                    cod=dat.__code__
                    lst=self.line_to_lambda_code[cod.co_firstlineno]
                    if cod not in lst:
                        lst.append(cod)
                        pretty_name += create_lambda_line_number(cod,self.line_to_lambda_code)

                encoded_val = ['FUNCTION', pretty_name, None]
                
                if get_parent:
                    enclosing_frame_id=get_parent(dat)
                    encoded_val[2]=enclosing_frame_id

                new_obj.extend(encoded_val)

            elif  typ is types.BuiltinFunctionType:
                pretty_name=get_name(dat)+'(...)'
                new_obj.extend(['FUNCTION', pretty_name, None])
            
            elif typ is types.ModuleType:
                new_obj.extend(['module', dat.__name__])

            elif typ in PRIMITIVE_TYPES:
                assert self.render_heap_primitives
                new_obj.extend(['HEAP_PRIMITIVE', type(dat).__name__, encode_primitive(dat)])

            else:
                typeStr=str(typ)
                m=typeRE.match(typeStr)

                if not m:
                    m=classRE.match(typeStr)

                assert m,typ
                encoded_dat=str(dat)
            
            return ret