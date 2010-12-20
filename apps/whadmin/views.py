# Create your views here.
# coding: utf-8
#
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from apps.core import get_skin_template
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.core.paginator import InvalidPage,EmptyPage
from django.http import HttpResponse
from django.template import Template,Context
from django.core import serializers
from apps.core.decorators import null_function
from apps.core.helpers import get_settings,paginate

def superuser_required(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        request = args[0]
        if request.user.is_superuser:
            return func(*args,**kwargs)
        else:
            return HttpResponseRedirect('/')
    return wrapper


@superuser_required
def index(request):
    template = get_skin_template(request.user,'index.html')
    return direct_to_template(request,template,{})

@null_function
def user_creation(request):
    pass

#@null_function
def rangs(request):
    template = get_skin_template(request.user,'rangs.html')
    return direct_to_template(request,template,{})
