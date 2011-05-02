# coding: utf-8
# Create your views here.
#from apps.core.shortcuts import direct_to_template
from django.http import HttpResponse
from anyjson import serialize as serialize_json

def xhr_mark_read(request, app_n_model, id):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'

    response.write(serialize_json({'status': True}))
    return response
