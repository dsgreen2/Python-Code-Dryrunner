from django.shortcuts import render
import json
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt

import logger

# Create your views here.
def index(request):
    return render(request,'index.html')



def finalizer_func(input_code,output_trace):
    
    ret=dict(code=input_code,trace=output_trace)
    json_output=json.dumps(ret,indent=None)
    return json_output


def dryrun(request):
    # code received from fronted  in code_input
    code_input=json.loads(request.body)
    raw_input_json=None

    # sending code to logger method. returned a trace to ans
    
    ans=logger.exec_script_str(code_input,raw_input_json,finalizer_func)
    return JsonResponse(ans,safe=False)


       #response_data=json.loads(request.body)
       #return JsonResponse(response_data,safe=False)

        
       







  