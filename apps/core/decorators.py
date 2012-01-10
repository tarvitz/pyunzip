# coding: utf-8
#
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from apps.core.models import Announcement
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_settings
from apps.core import get_skin_template
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError
from apps.core.handlers import UploadProgressHandler

"""
def can_post_articles(func, *args, **kwargs):
    def wrapper(args, kwargs):
        request = kwargs['request']
        permissions = kwargs['permissions']
        user = request.user
        if user.is_superuser or user.is_staff or user.user_permissions(
    return wrapper
"""
def null(func):
    def wrapper(*args, **kwargs):
        return ''
    return wrapper


def has_permission(perms):
    """checks if request.user has permission"""
    permissions = perms
    def decorator(func):
        def wrapper(request,*args,**kwargs):
            user = request.user
            perms = user.get_all_permissions()
            if not user.is_active:
                return HttpResponseRedirect(reverse('auth_login',None,{}))
            #superuser is SUPER USER!
            if user.is_superuser:
                return func(request,*args,**kwargs)
            #TODO: Add code to implement group permissions o_O

            if permissions in [i for i in perms]:
                return func(request,*args,**kwargs)
            else:
                login = reverse('auth_login',None,{})
                return HttpResponseRedirect(login)
        return wrapper
    return decorator
            
#returns referer
def null_function(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        request = args[0]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    return wrapper

#deprecated
def update_subscription(func,*args,**kwargs):
    def wrapper(*args,**kwargs):
        request = args[0]
        id,number = None,None
        app_label,model = None,None
        if 'id' in kwargs:
            id = kwargs['id']
        if 'number' in kwargs:
            number = kwargs['number']
        id = id or number
        if 'object_model' in kwargs:
            app_label,model = kwargs['object_model'].split('.')
        
        user = request.user
        auto_update_subscription = get_settings(user,'auto_update_subscription',False)
        if auto_update_subscription:
            #TODO: FIXATE getting Announcement through app_label and model
            if app_label and model:
                ct = ContentType.objects.get(app_label=app_label,model=model)
                try:
                    announcement = Announcement.objects.get(content_type=ct,object_pk=str(id))
                    if request.user.is_authenticated():
                        announcement.update(user)
                except Announcement.DoesNotExist:
                    pass
                    
            else:
                announcements = Announcement.objects.filter(notified_users=user,object_pk=str(id))
                if announcements:
                    for a in announcements:
                        a.update(user)
        return func(*args,**kwargs)
    return wrapper

def update_subscription_new(app_model,pk_field='id'):
    def decorator(func):
        def wrapper(*args,**kwargs):
            if pk_field in kwargs:
                pk = kwargs[pk_field]
            else:
                raise TemplateSyntaxError, "there is no 'pk' in the follow view" 
            app_label,model = app_model.split('.')
            request = args[0]
            user = request.user 
            if not user.is_authenticated():
                return func(*args,**kwargs)
            ct = ContentType.objects.get(app_label=app_label,model=model)
            auto_update_subscription = get_settings(user,'auto_update_subscription', False)
            if auto_update_subscription:
                #implement: get_404_or_none
                try:
                    announcement = Announcement.objects.get(content_type=ct,object_pk=str(pk))
                    announcement.update(user)
                except Announcement.DoesNotExist:
                    pass
            return func(*args,**kwargs)

        return wrapper

    return decorator

def benchmarking(func):
    def wrapper(*args,**kwargs):
        request = args[0]
        from datetime import datetime
        setattr(request,'_now_',datetime.now())
        return func(*args,**kwargs)
    return wrapper

#overriding of vanilla render_to
def render_to(template_path):
    """
    Expect the dict from view. Render returned dict with
    RequestContext.
    """
    
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            #import pdb
            #output = pdb.runcall(func, request, *args, **kwargs)
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            kwargs = {'context_instance': RequestContext(request)}
            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')
            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
            else:
                template = get_skin_template(request.user,template_path)
            return render_to_response(template, output, **kwargs)
        return wrapper

    return decorator

def progress_upload_handler(func):
    def wrapper(*args,**kwargs):
        request = args[0]
        progress_id = request.GET.get('X-Progress-ID',None)
        request.upload_handlers.insert(0,UploadProgressHandler(request,progress_id))
        return func(*args,**kwargs)
    return wrapper


def check_user_fields(parse_dict):
    """ check user field states """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return func(request, *args, **kwargs)
            for key in parse_dict.keys():
                if not parse_dict[key] != getattr(request.user, key):
                    return HttpResponseRedirect(reverse('url_permission_denied'))
                return func(request, *args, **kwargs)
        return wrapper
    return decorator

def lock_with_dev(parse_dict):
    """ locks view if giving settings aint equal given ones"""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            for key in parse_dict.keys():
                have_key = hasattr(settings, key)
                if not have_key or parse_dict[key] != getattr(settings, key):
                    return HttpResponseRedirect(
                        reverse('url_currently_unavailable'))
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
