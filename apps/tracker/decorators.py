# coding: utf-8
#
from apps.tracker.models import SeenObject
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_content_type,get_content_type_or_none

def new_comment(func):
    def wrapper(*args,**kwargs):
        request = args[0]
        if request.method == 'POST':
            app_n_model = request.POST.get('app_n_model','')
            obj_id = request.POST.get('obj_id','')
            if app_n_model and obj_id:
                ct = get_content_type_or_none(app_n_model)
                try:
                    obj = ct.model_class().objects.get(pk=str(obj_id))
                except:
                    return func(*args,**kwargs)
                SeenObject.objects.filter(content_type=ct,object_pk=str(obj_id)).delete()
                so = SeenObject(content_type=ct,object_pk=str(obj_id),user=request.user)
                so.save()
                return func(*args,**kwargs)
        else:
            return func(*args,**kwargs)
        return func(*args,**kwargs)
    return wrapper
#obsolete
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
            print "user_visit decorator initialized"
            request = args[0]
            if not request.user.is_authenticated():
                print "not authenticated"
                return func(*args,**kwargs)
            if obj is None and (object_pk is None or ct is None):
                print "nothing have passed"
                return func(*args, **kwargs)
            if obj:
                pk = obj.pk
                from apps.core.helpers import get_content_type_or_none
                content_type = get_content_type_or_none(obj)
            else:
                pk = kwargs[object_pk]
                app_label,model = ct.split('.')
                from apps.core.helpers import get_object_or_none
                content_type = get_object_or_none(ContentType,app_label=app_label,
                    model=model)
            print "ct: %r" % content_type
            if content_type:
                so = SeenObject.objects.filter(content_type=content_type,
                    object_pk=str(pk),
                    user=request.user)
                print "so exists, so: %r" % so
                if not so: #includes nothiing
                    print "saving.."
                    so = SeenObject(content_type=content_type,object_pk=str(pk),
                        user=request.user)
                    so.save()
            return func(*args,**kwargs)
        return wrapper
    return fnc


