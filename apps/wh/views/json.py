# coding: utf-8
from django.http import HttpResponse
from django.core import serializers
from apps.wh.models import MiniQuote, Army, Expression
from apps.core.helpers import render_to, render_to_json

def miniquote(request):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    try:
        mq = MiniQuote.objects.order_by('?')[0]
    except IndexError:
        response.write('false')
        return response
    response.write(serializers.serialize("json",[mq]))

    return response

def army(request, id=None):
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    if not id:
        response.write("[]")
        return response
    armies = Army.objects.filter(side__id=id)
    response.write(serializers.serialize("json", armies))
    return response

@render_to_json(content_type='application/json')
def expression(request):
    return {
        'expression': Expression.objects.order_by('?').all()[0]
    }
