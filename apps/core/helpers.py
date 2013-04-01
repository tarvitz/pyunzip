# coding: utf-8
#
import os
from datetime import datetime, timedelta, date, time
#from apps.core.forms import CommentForm
from functools import partial
from django.http import HttpResponseRedirect, HttpResponse
from apps.core import get_skin_template
from apps.core.shortcuts import direct_to_template
from django.shortcuts import (
    render_to_response, get_object_or_404 as _get_object_or_404,
    redirect
)
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.comments.models import Comment
from django.contrib.auth.models import User, AnonymousUser
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.core.paginator import InvalidPage,EmptyPage
from django.core.urlresolvers import reverse
from django.template.loader import get_template, TemplateDoesNotExist
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from celery.task import task
from django.utils.translation import ugettext_lazy as _, ugettext as tr
import simplejson as json
import bz2
import re
import logging
logger = logging.getLogger(__name__)

send_email_message = task()(send_mail)

IM_TEXT="""
user '%s' has left comment on '%s%s?page=last'
Please visit this page to figure out that have been done there.
"""
EMAIL_TEXT = """"""

# safe method get obj.attr.attr1 and so on
# safe_ret(cell, 'room.pk')
# safe_ret(cell, 'room.base.pk')
safe_ret = (
    lambda x, y: reduce(
        lambda el, attr: (
            getattr(el, attr)() if callable(getattr(el, attr)) else getattr(el, attr)
        )
        if hasattr(el, attr) else None,
        [x, ] + y.split('.')
    )
)

get_int_or_zero = lambda x: int(x) if (
    x.isdigit() if isinstance(x, basestring) else x
) else 0

#TODO: OVERWRITE IT =\
#instance is the object passing through the signal
def send_notification(instance,**kwargs):
    from apps.core.models import Announcement
    #comment-instance like object
    if hasattr(instance,'content_type') and hasattr(instance,'object_pk'):
        #
        #getting real object
        real_object = instance.content_type.model_class().objects.get(pk=str(instance.object_pk))
        #do anything we want to do ;)
        #print real_object
        # do notification
        # DO NOT FORGET THAT Primary info contained in instance object not in real, we just test if real object has user that shoud be
        # announcemented
        try:
            announcement = Announcement.objects.get(content_type=instance.content_type,object_pk=str(instance.object_pk))
            for user in announcement.users.distinct():
                #sending notification
                #it would be wise to do not notify yourself :)
                if 'user_field' in kwargs:
                    instance_user = getattr(instance,kwargs['user_field'])
                else:
                    instance_user = instance.user
                if not instance_user.is_authenticated():
                    return
                if 'content_field' in kwargs:
                    content = getattr(instance,kwargs['content_field'])
                else:
                    content = instance.get_content()
                if callable(content): content = content()

                if instance_user != user:
                    announcement.notified(user)
                    text_content = tr(IM_TEXT %
                        (instance_user.nickname,settings.GLOBAL_SITE_NAME,real_object.get_absolute_url()))
                    #OBSOLETE
                    notify_jid = user.settings.get('notify_jid', False)
                    notify_email = user.settings.get('notify_email', True)
                    if user.email and notify_email:
                        send_email_message.delay(_('WarMist no-replay notification'),text_content,settings.FROM_EMAIL,
                            [user.email],fail_silently=False,
                            auth_user=settings.EMAIL_HOST_USER,
                            auth_password=settings.EMAIL_HOST_PASSWORD)
                    if user.jid and notify_jid:
                        message = "s_notify jid:%s message:%s" % (user.jid,text_content)
                        send_network_message.delay('localhost', 40001, message)
                    #we should make it async :(
                    #from time import sleep
                    #sleep(60)
                    #TODO: implement here notification sending
                    #print user
                    #move notified user in the notified list
                #pass
        except Announcement.DoesNotExist:
            #do nothing
            pass
        #print "do notification for %r" % real_object
    #real object still not tested
    #TODO: test it?
    else:
        #do notification here
        #print instance
        try:
            model_name = object.__class__.__doc__.split('(')[0].lower()
            # TODO:
            #app_label =
            try:
                content_type = ContentType.objects.get(model=model_name)
                object_pk = instance.pk
            except (ContentType.DoesNotExist,ContentType.MultipleObjectsReturned):
                # Probably there is Multiply objects, need to implement app_label extraction before fixing it
                return
            announcement = Announcement.objects.get(content_type=content_type,object_pk=str(object_pk))
            for user in  announcement.users.distinct():
                announcement.notified(user)
                #sending notification for a user from userlist
                #print user
        except Announcement.DoesNotExist:
            #nothing to do? :)
            pass
        #print "do notification for %r" % instance

def get_object_or_none(Object, **kwargs):
    try:
        obj = Object.objects.get(**kwargs)
        return obj
    except:
        return None
    return None
get_object_or_None = get_object_or_none

def get_settings(user,settings,default=False):
    if hasattr(user, 'settings'):
        return user.settings.get(settings, default) if \
            user.settings else default
    else:
        return default

# decorator
def can_act(func):
    def wrapper(request,*args,**kwargs):
        user = request.user
        perms = user.get_all_permissions()
        if user.is_superuser or user.is_staff:
            return func(request,*args,**kwargs)
        from apps.wh.models import Warning
        warning = get_object_or_none(Warning,user=request.user)
        if warning:
            if int(warning.level) >= settings.READONLY_LEVEL:
                return HttpResponseRedirect('/you/can/not/act/')
        return func(request,*args,**kwargs)
    return wrapper

"""
#obsolete, moved to views with another level functionallity
@login_required
@can_act
def save_comment(request,template,vars,ct=None,object_pk=None,redirect_to=None):
    if request.method == 'POST':
        form = CommentForm(request.POST,request=request)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            syntax = form.cleaned_data.get('syntax',None)
            hidden_syntax = form.cleaned_data.get('hidden_syntax',None)
            subscribe = form.cleaned_data.get('subscribe',False)
            unsubscribe = form.cleaned_data.get('unsubscribe',False)
            if not syntax:
                if hidden_syntax: syntax = hidden_syntax
                else: syntax = settings.SYNTAX[0][0] #the default syntax is at the top of the list

            #adding user to announcement table
            #if Announcement 's already exist for this object
            try:
                announcement = Announcement.objects.get(content_type=ct,object_pk=str(object_pk))
                #if subscribed we gonna subscribe him or she :)
                if subscribe:
                    announcement.update(request.user)
                    announcement.save()
                #update notification readiness
                if request.user in announcement.notified_users.distinct():
                    announcement.update(request.user)

            #there is no any users for their announcement s
            except Announcement.DoesNotExist:
                if subscribe:
                    announcement = Announcement(content_type=ct,object_pk=str(object_pk))
                    #saving users before saving announcement
                    announcement.save()
                    announcement.users.add(request.user)
                    announcement.save()
            #end of Announcement

            #kind of danger :)
            try:
                c = Comment.objects.filter(
                    content_type=ct,object_pk=str(object_pk)
                    ).order_by('-id')[0]
                if c.user == request.user:
                    if c.comment != comment:
                        now = datetime.now().__format__('%H:%M:%S')
                        c.comment = c.comment + '\n\n[upd %s]' % now + comment
                        # I think i'd be great idea to do not change the syntax
                        # withing composing old comment and new one
                        #c.syntax = syntax
                        c.save()
                    #do nothing if we're trying to pass the same comment :)
                    else:
                        pass
                else:
                    c = Comment(content_type=ct,object_pk=str(object_pk),
                        comment=comment,
                        user=request.user,is_public=True,
                        site_id=1,submit_date=datetime.now(),
                        syntax=syntax)
                    c.save()
                if redirect_to:
                    return {'success':True,'redirect':redirect_to}
                else:
                    return {'success':True,'redirect':request.META.get('HTTP_REFERER','/')}
            #there is no comments at all
            except IndexError:
                c = Comment(content_type=ct,object_pk=str(object_pk),comment=comment,
                        user=request.user,is_public=True,site_id=1,submit_date=datetime.now(),syntax=syntax)
                c.save()
                if redirect_to:
                    return {'success':True,'redirect':redirect_to}
                else:
                    return {'success': True,'redirect':request.META.get('HTTP_REFERER','/')}
        else:
            vars.update({'form':form})
            return {'success':False,'form':form}
    else:
        return {}
"""

def send_email(email,content,**kwargs):
   pass

def purge_unexistable_comments():
    pass



#TODO implement code below with kwargs passing style
def get_user(username=None,nickname=None,id=None):
    if username:
        try:
            user = User.objects.get(username__iexact=username)
            return user
        except User.DoesNotExist:
            return None
    if nickname:
        try:
            user = User.objects.get(nickname__iexact=nickname)
            return user
        except User.DoesNotExist:
            return None
    if id:
        try:
            user = User.objects.get(id__exact=id)
            return user
        except User.DoesNotExist:
            return None

def get_content_type(Object):
    """works with ModelBase based classes, its instances
    and with format string 'app_label.model_name'
    retrieves content_type or raise the common django Exception
    Examples:
    get_content_type(User)
    get_content_type(onsite_user)
    get_content_type('auth.user')
    """
    #print Object
    if callable(Object): #class
        #print "class: ", Object
        #retrieving content_type from class object
        model = Object.__name__.lower()
        app_label = (x for x in reversed(Object.__module__.split('.')) if x not in 'models').next()
        #ct = ContentType.objects.get(app_label=app_label,model=model)
    elif hasattr(Object,'pk'): #class instance
        #print "class instance: ", Object
        if hasattr(Object, '_sphinx') or hasattr(Object, '_current_object'):
            app_label = (x for x in reversed(Object._current_object.__module__.split('.')) if x not in 'models').next()
            model = Object._current_object.__class__.__name__.lower()
        else:
            app_label = (x for x in reversed(Object.__module__.split('.')) if x not in 'models').next()
            model = Object.__class__.__name__.lower()
        #ct = ContentType.objects.get(app_label=app_label,model=model)
        #model =
    elif isinstance(Object,str) or isinstance(Object,unicode):
        #print "str: ", Object
        #retrieving content_type from string format 'app_label.model'
        app_label,model = Object.split('.')
    ct = ContentType.objects.get(app_label=app_label,model=model)
    return ct

def get_content_type_or_none(Object):
    try:
        ct = get_content_type(Object)
        return ct
    except:
        return None

def get_comments(Object,**kwargs):
    #model = Object.__name__.lower()
    #app_label_raw = Object.__module__
    #app_label_raw = app_label_raw[:app_label_raw.rindex('.models')]
    #_len = len(app_label_raw.split('.'))
    #app_label = app_label_raw.split('.')[_len-1]
    #ct = ContentType.objects.get(app_label=app_label,model=model)
    ct = get_content_type(Object)
    comments = Comment.objects.filter(content_type=ct,**kwargs)
    return comments

def paginate(Objects,page,**kwargs):
    if 'pages' in kwargs: _pages_ = kwargs['pages']
    else: _pages_ = 20 #by default
    #print page,isinstance(page,int)
    paginator = Paginator(Objects,_pages_)
    #?page=last goes for the last page
    if isinstance(page,str) or isinstance(page,unicode):
        if page in ('last','end'): page = paginator.num_pages
    try:
        objects = paginator.page(page)
    except (EmptyPage,InvalidPage):
        objects = paginator.page(1)
    if 'jump' in kwargs: objects.jump = kwargs['jump']
    if 'model' in kwargs:
        objects.model = kwargs['model']
    if 'raw_model' in kwargs:
        objects.raw_model = kwargs['raw_model']
    if 'view' in kwargs: objects.view = kwargs['view']

    return objects

def get_template_or_none(template,plain=False):
    try:
        t = get_template(template)
        if plain:
            return template
        else:
            return t
    except TemplateDoesNotExist:
        return None

def validate_object(app_n_label,obj_id):
    app_label,model = app_n_label.split('.')
    try:
        ct = ContentType.objects.get(app_label=app_label,model=model)
        ct.model_class().objects.get(pk=str(obj_id))
        return True
    except:
        return False

def handle_uploaded_file(f,path,compress=False):
    from django.conf import settings
    fp_path = os.path.join(settings.MEDIA_ROOT,path)
    os.path.exists(fp_path) or os.makedirs(fp_path) #equivalent to if statement
    f_name = re.sub(re.compile(r'\(|\ |\)|!|\'|\"|\?|:|\+|}|{|\^|\%|\$|\#|@|~|`|,', re.S ),'_',f.name)
    f_name = re.sub(re.compile(r'_+'),'_',f_name)

    fp_path = os.path.join(fp_path,f_name)
    #print "fp_path: ", fp_path
    fp = open(fp_path,'wb+')
    """
    if compress:
        fp_path += '.bz2'
        compressor = bz2.BZ2Compressor(7)
        for chunk in f.chunks():
            compressor.compress(chunk)
        data = compressor.flush()
        open(fp,'wb+').write(data)
    else:
    """
    for chunk in f.chunks():
        fp.write(chunk)
    #print "filename: ", os.path.join(path,f.name)
    return os.path.join(path,f_name)

def get_upload_form(path):
    from apps.core.settings import UPLOAD_SETTINGS
    try:
        _module_ = UPLOAD_SETTINGS[path]['form']
        _mod_ = _module_[:_module_.rindex('.')]
        _form_ = _module_[_module_.rindex('.')+1:]
        _module_ = __import__(_mod_,{},{},[''],0)
        return getattr(_module_,_form_)
    except:
        return None

def get_upload_helper(path):
    from apps.core.settings import UPLOAD_SETTINGS
    try:
        mod = UPLOAD_SETTINGS[path]['helper']
        m = mod[:mod.rindex('.')]
        helper = mod[mod.rindex('.')+1:]
        module = __import__(m,{},{},[''],0)
        return getattr(module,helper)
    except:
        return None

@task
def send_network_message(host,port,message):
    import socket
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,port))
        sock.send(message)
        sock.close()
        return True
    except:
        logger.error('Could not send message')
        return False

def get_content_type_new(Object):
    """
    works with ModelBase based classes, its instances
    and with format string 'app_label.model_name', also supports
    sphinx models and instances modification
    source taken from warmist helpers source
    retrieves content_type or raise the common django Exception
    Examples:
    get_content_type(User)
    get_content_type(onsite_user)
    get_content_type('auth.user')
    """

    if callable(Object):  # class
        model = Object._meta.module_name
        app_label = Object._meta.app_label
        #model = Object.__name__.lower()
        #app_label = (x for x in reversed(
        #    Object.__module__.split('.')) if x not in 'models').next()

    elif hasattr(Object, 'pk'):  # class instance
        if hasattr(Object, '_sphinx') or hasattr(Object, '_current_object'):
            model = Object._current_object._meta.module_name
            app_label = Object._current_object._meta.app_label
            #app_label = (x for x in reversed(
            #    Object._current_object.__module__.split('.')) \
            #if x not in 'models').next()
            #model = Object._current_object.__class__.__name__.lower()
        else:
            app_label = Object._meta.app_label
            model = Object._meta.module_name
            #app_label = (x for x in reversed(Object.__module__.split('.')) \
            #if x not in 'models').next()
            #model = Object.__class__.__name__.lower()
    elif isinstance(Object, basestring):
        app_label, model = Object.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return ct


def get_content_type_or_None(Object):
    try:
        return get_content_type_new(Object)
    except:
        return None


def make_http_response(**kw):
    response = HttpResponse(status=kw.get('status', 200))
    response['Content-Type'] = kw.get('content_type', 'text/plain')
    if 'content' in kw:
        response.write(kw['content'])
    return response

def model_json_encoder(obj, **kwargs):
    from django.db.models.base import ModelState
    from django.db.models import Model
    from django.db.models.query import QuerySet
    from decimal import Decimal
    from django.db.models.fields.files import ImageFieldFile
    from django import forms
    from django.utils.functional import Promise
    is_human = kwargs.get('parse_humanday', False)
    if isinstance(obj, QuerySet):
        return list(obj)
    elif isinstance(obj, Model):
        dt = obj.__dict__
        #obsolete better use partial
        fields = ['_content_type_cache', '_author_cache', '_state']
        for key in fields:
            if key in dt:
                del dt[key]
        #normailize caches
        disable_cache = kwargs['disable_cache'] \
            if 'disable_cache' in kwargs else False

        # disable cache if disable_cache given
        for key in dt.keys():
            if '_cache' in key and key.startswith('_'):
                if not disable_cache:
                    dt[key[1:]] = dt[key]
                    #delete cache
                    del dt[key]
            if disable_cache and '_cache' in key:
                del dt[key]

        #delete restriction fields
        if kwargs.get('fields_restrict'):
            for f in kwargs.get('fields_restrict'):
                if f in dt:
                    del dt[f]
        #make week more humanic
        if is_human and 'week' in dt:
            dt['week'] = unicode(humanday(dt['week']))
        return dt
    elif isinstance(obj, ModelState):
        return 'state'
    elif isinstance(obj, datetime):
        return [
            obj.year, obj.month, obj.day,
            obj.hour, obj.minute, obj.second,
            obj.isocalendar()[1]
        ]
    elif isinstance(obj, date):
        return [obj.year, obj.month, obj.day]
    elif isinstance(obj, time):
        return obj.strftime("%H:%M")
    elif isinstance(obj, ImageFieldFile):
        return obj.url if hasattr(obj, 'url') else ''
    elif isinstance(obj, forms.ModelForm) or isinstance(obj, forms.Form):
        _form = {
            'data': obj.data if hasattr(obj, 'data') else None,
            # may catch Does not exists
            #'instance': obj.instance if hasattr(obj, 'instance') else None,
        }
        if obj.errors:
            _form.update({'errors': obj.errors})
        return _form
    elif isinstance(obj, Promise):
        return unicode(obj)
    #elif isinstance(obj, Decimal):
    #    return float(obj)
    return obj


def get_model_instance_json(Obj, id):
    instance = get_object_or_None(Obj, id=id)
    response = make_http_response(content_type='text/javascript')
    if not instance:
        response.write(json.dumps({
            'success': False,
            'error': unicode(_("Not found")),
        }, default=model_json_encoder))
        return response
    response.write(json.dumps({
        'success': True,
        'instance': instance,
    }, default=model_json_encoder))
    return response

def render_to_json(content_type='application/json', is_mongo=False):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            dt = func(request, *args, **kwargs)
            response = make_http_response(content_type=content_type)
            encoder = partial(model_json_encoder, is_mongo=is_mongo)
            response.write(json.dumps(dt, default=encoder))
            return response
        return wrapper
    return decorator

def render_to(template, allow_xhr=False, content_type='text/html'):
    _content_type = content_type
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            response = make_http_response(content_type='application/json')
            dt = func(request, *args, **kwargs)
            if not isinstance(dt, dict):
                raise ImproperlyConfigured("render_to should take dict instance not %s" % type(dt))
            # overrides
            tmpl = get_skin_template(request.user, dt.get('_template', template))

            content_type = dt.get('_content_type', _content_type)

            force_ajax = request.META.get('HTTP_X_FORCE_XHTTPRESPONSE', None)
            if 'redirect' in dt:
                if force_ajax:
                    response.write(json.dumps({"status": "ok"}))
                    return response

                args = dt.get('redirect-args', [])
                if args:
                    redr = reverse(dt['redirect'], args=args)
                    return redirect(redr)
                return redirect(dt['redirect'])

            if content_type.lower() == 'text/html':
                if force_ajax and allow_xhr:
                    response.write(json.dumps(dt, default=model_json_encoder))
                    return response
                return render_to_response(
                    tmpl,
                    dt,
                    context_instance=RequestContext(request))

            elif content_type.lower() == 'text/csv':
                response = make_http_response(content_type=content_type)
                response['Content-Disposition'] = 'attachment; filename="export.csv"'
                response.write(
                    render_to_string(tmpl, dt)
                )
                return response

            elif content_type.lower() in ('text/json', 'text/javascript',
                                          'application/json'):
                response = HttpResponse()
                response['Content-Type'] = content_type
                tmpl = get_template(tmpl)
                response.write(tmpl.render(Context(dt)))
                return response
            else:
                return render_to_response(
                    tmpl,
                    dt, context_instance=RequestContext(request))
        return wrapper
    return decorator

def post_markup_filter(string):
    r = re.compile(r'\((?P<tag>\w+)\)\[(?P<text>.*?)\]', re.M|re.I|re.S)
    result = r.findall(string)
    for (tag, text) in result:
        if tag not in ('spoiler', 'off'):
            continue
        if tag == 'spoiler':
            html = render_to_string('s_comments.html', {'spoiler_text': text})
        elif tag == 'off':
            html = render_to_string('off_comments.html', {'offtopic_text': text})
        html = re.sub(r'\n+', '', html)
        string = string.replace('(%s)[%s]' % (tag, text), html)
    # quote
    r = re.compile(
        r'\((?P<user>[\w\d\-\ ]+)\){(?P<quote>.*?)}',
        re.UNICODE|re.MULTILINE|re.DOTALL|re.IGNORECASE
    )

    result = r.findall(string)
    for (username, text) in result:
        user = get_object_or_None(User, nickname__iexact=username) or AnonymousUser()
        html = render_to_string('q_comments.html', {'quote_user': user, 'quote_text': text})
        html = re.sub(r'\n+', '', html)
        string = string.replace('(%s){%s}' % (username, text), html)
    string = string.replace('(cut)', '')
    return string

def unescape(string):
    string = string.replace('&lt;', '<')
    string = string.replace('&gt;', '>')
    return string

def render_filter(value, arg):
    from apps.thirdpaty.postmarkup import render_bbcode
    from apps.thirdpaty.creole.shortcuts import creole_filter as render_creole
    from apps.thirdpaty.textile import render_textile
    from django.utils.safestring import mark_safe

    syntaxes = [i[0] for i in settings.SYNTAX]
    if arg in syntaxes:
        if arg in 'bb-code':
            return unescape(render_bbcode(value))
        elif arg in 'creole' or arg in 'wiki':
            return creole_filter(value)
        elif arg in 'textile':
            return render_textile(value)
        elif arg in 'markdown':
            return spadvfilter(value)
    return render_textile(value)
