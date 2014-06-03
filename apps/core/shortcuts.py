# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext


def direct_to_template(request, template, context=None, processors=None):
    context = context or {}
    processors = processors or ()
    return render_to_response(
        template, context,
        context_instance=RequestContext(request, processors=processors)
    )
