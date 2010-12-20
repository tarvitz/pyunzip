# coding: utf-8
#from django.http import HttpResponse
#from django.template.loader import get_template
from apps.wh.models import Warning 
from datetime import datetime,timedelta
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

class WarningsMiddleware(object):
    def process_request(self, request):
        warnings = Warning.objects.all()
        for w in warnings:
            if w.expired<datetime.now():
                w.user.is_active = True
                w.user.save()
                #also we delete message for the warning
                ct = ContentType.objects.get(app_label='wh',model='warning')
                comments = Comment.objects.filter(content_type=ct,object_pk=str(w.pk))
                for c in comments:
                    c.delete()
                w.delete()
            #ban
            if w.level == 7 and not w.user.is_superuser:
                w.user.is_active = False
                w.user.save()
            #permanent ban
            if w.level == 8 and not w.user.is_superuser:
                w.expired = datetime.now()+timedelta(days=365*10) #ten years
                w.user.is_active = False
                w.user.save()
