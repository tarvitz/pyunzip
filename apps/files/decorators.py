# coding: utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic.simple import direct_to_template
#decorators ARE here

def can_purge_replays(func,*args,**kwargs):
    def wrapper(*args, **kwargs): 
        request = args[0]
        user = request.user
        if user.user_permissions.filter(codename='purge_replays') or user.is_superuser or user.is_staff:
            return func(*args,**kwargs)
        else:
            return HttpResponseRedirect('/permission/denied/')
    return wrapper

#end of decorators

