# coding: utf-8
#
from apps.tracker.models import SeenObject
from django.contrib.contenttypes.models import ContentType

def user_add_content(obj=None,object_pk=None,ct=None):
    def fnc(func):
        def wrapper(*args,**kwargs):
            if obj is None and (object_pk is None or ct is None):
                return fnc(*args,**kwargs)
            if obj:
                pk = obj.pk
                from apps.core.helpers import get_content_type_or_none
                content_type = get_content_type_or_none(obj) #may cause trouble :
            else:
                pk = kwargs[object_pk]
                content_type = kwargs[ct]
            request = args[0]
            #cleanse trouble cases
            if content_type:
                soes = SeenObject.objects.filter(content_type=content_type,
                    object_pk=str(pk))
                soes.delete()
                
                so = SeenObject(content_type=content_type,
                    object_pk=str(pk),user=request.user)
                so.save()
            return func(*args, **kwargs)
        return wrapper
    return fnc

def user_visit(obj=None,object_pk=None,ct=None):
    def fnc(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.user.is_anonymous:
                return func(*args,**kwargs)
            if obj is None and (object_pk is None or ct is None):
                return fnc(*args, **kwargs)
            if obj:
                pk = obj.pk
                from apps.core.helpers import get_content_type_or_none
                content_type = get_content_type_or_none(obj)
            else:
                pk = kwargs[object_pk]
                app_label,model = ct.split('.')
                content_type = ContentType.objects.get(app_label=app_label,model=model)
            if content_type:
                so = SeenObject.objects.filter(content_type=content_type,object_pk=str(pk),
                    user=request.user)
                if len(so) == 0:
                    so = SeenObject(content_type=content_type,object_pk=str(pk),
                        user=request.user)
                    so.save()

            return func(*args,**kwargs)
        return wrapper
    return fnc


