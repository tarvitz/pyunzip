# coding: utf-8
# Create your views here.
#from apps.core.shortcuts import direct_to_template
from django.http import HttpResponse
from anyjson import serialize as serialize_json
from apps.core.helpers import get_content_type
from apps.tracker.models import SeenObject
from django.contrib.contenttypes.models import ContentType
from apps.core.decorators import login_required_json

@login_required_json
def xhr_mark_read(request, app_n_model, id):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    ct = get_content_type(app_n_model)
    if ct:
        try:
            obj = ct.model_class().objects.get(pk=str(id))
        except:
            response.write(serialize_json({'status': False}))
            return response
    try:
        so = SeenObject.objects.get(content_type=ct, object_pk=str(id),
            user=request.user)
    except SeenObject.DoesNotExist:
        so = SeenObject(content_type=ct, object_pk=str(id), user=request.user)
        so.save()
    response.write(serialize_json({'status': True}))
    return response
