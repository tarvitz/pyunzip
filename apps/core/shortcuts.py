# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext

#overrides deprecated direct_to_template to new more complicant one solution \
def direct_to_template(request,template,context={}):
    return render_to_response(template,context,
        context_instance=RequestContext(request))
