# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext


def direct_to_template(request, template, context={}, processors=()):
    return render_to_response(
        template, context,
        context_instance=RequestContext(request, processors=processors)
    )
