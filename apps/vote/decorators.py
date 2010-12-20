# coding: utf-8
from django.http import HttpResponseRedirect

def vote_allow_objects(lst):
    def decorator(func):
        def wrapper(request,*args,**kwargs):
            if 'model_name' in kwargs:
                model_name = kwargs['model_name']
                if model_name in lst:
                    return func(request,*args,**kwargs)
                else:
                    return HttpResponseRedirect('/vote/invalid/object/')
            else:
                return HttpResponseRedirect('/vote/invalid/object/')
        return wrapper
    return decorator
