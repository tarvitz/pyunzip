# coding: utf-8

import six

from functools import wraps
from datetime import datetime, date, time
from functools import partial

from apps.comments.models import Comment
from apps.core import get_skin_template
from apps.thirdpaty.textile import render_textile
from apps.helpers.diggpaginator import DiggPaginator as Paginator

from django.http import HttpResponse, Http404
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.shortcuts import (
    render_to_response, redirect
)
from django.template import RequestContext
from django.template.loader import render_to_string

from django.contrib.auth.models import AnonymousUser

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.db.models import get_model

from django.core.exceptions import ImproperlyConfigured
from django.template import Context

import simplejson as json
import re
import logging
logger = logging.getLogger(__name__)


IM_TEXT = """
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
            getattr(el, attr)() if callable(getattr(el, attr))
            else getattr(el, attr)
        )
        if hasattr(el, attr) else None,
        [x, ] + y.split('.')
    )
)


get_int_or_zero = lambda x: int(x) if (
    x.isdigit() if isinstance(x, six.string_types) else x
) else 0


# noinspection PyPep8Naming
def get_object_or_None(object_source, *args, **kwargs):
    if isinstance(object_source, six.string_types):
        object_source = get_model(*object_source.split('.'))
    try:
        return _get_object_or_404(object_source, *args, **kwargs)
    except (Http404, MultipleObjectsReturned):
        return None


def get_object_or_404(object_source, *args, **kwargs):
    """Retruns object or raise Http404 if it does not exist"""
    try:
        if hasattr(object_source, 'objects'):
            return object_source.objects.get(*args, **kwargs)
        elif hasattr(object_source, 'get'):
            return object_source.get(*args, **kwargs)
        else:
            raise Http404("Giving object has no manager instance")
    except (object_source.DoesNotExist, object_source.MultipleObjectReturned):
        raise Http404("Object does not exist or multiple object returned")


def get_content_type_or_none(object_source):
    try:
        ct = get_content_type(object_source)
        return ct
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        return None


def get_comments(object_source, **kwargs):
    """
    get comments for ModelBase class, instance, format string
    'app_label.model_name'

    :param object_source: ModelBase class, ModelBase instance, format string
    :param kwargs:
    :return: Comments queryset
    :rtype: QuerySet
    """

    ct = get_content_type(object_source)
    comments = Comment.objects.filter(content_type=ct, **kwargs)
    return comments


def paginate(objects, page, **kwargs):
    _pages = kwargs.get('pages', settings.OBJECTS_ON_PAGE)

    paginator = Paginator(objects, _pages)
    #?page=last goes for the last page
    if isinstance(page, six.string_types):
        if page in ('last', 'end'):
            page = paginator.num_pages
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(1)

    map_fields = ['jump', 'model', 'view', 'raw_model']
    # objects.jump = kwargs.get('jump', None)
    for field in map_fields:
        setattr(objects, field, kwargs.get(field, None))
    return objects


# noinspection PyProtectedMember,PyUnresolvedReferences
def get_content_type(object_source):
    """
    works with ModelBase based classes, its instances
    and with format string 'app_label.model_name', also supports
    sphinx models and instances modification
    source taken from warmist helpers source
    retrieves content_type or raise the common django Exception
    Examples:
    .. code-block:: python

        get_content_type(User)
        get_content_type(onsite_user)
        get_content_type('auth.user')

    works with ModelBase based classes, its instances
    and with format string 'app_label.model_name'
    retrieves content_type or raise the common django Exception

    :param object_source: object, ModelBase class or format string
    'app_label.model_name'
    :return: ContentType ``instance``
    :rtype: ContentType
    """
    app_label, model = (None, None)
    if callable(object_source):  # class
        model = object_source._meta.module_name
        app_label = object_source._meta.app_label

    elif hasattr(object_source, 'pk'):  # class instance
        if hasattr(object_source, '_sphinx') or hasattr(object_source,
                                                        '_current_object'):
            model = object_source._current_object._meta.module_name
            app_label = object_source._current_object._meta.app_label
        else:
            app_label = object_source._meta.app_label
            model = object_source._meta.module_name
    elif isinstance(object_source, basestring):
        app_label, model = object_source.split('.')
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return ct


# noinspection PyPep8Naming
def get_content_type_or_None(object_source):
    try:
        return get_content_type(object_source)
    except (MultipleObjectsReturned, ObjectDoesNotExist):
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

    from django.db.models.fields.files import ImageFieldFile, FieldFile
    from django import forms
    from django.utils.functional import Promise
    from sorl.thumbnail.images import ImageFile as SorlImageFile

    if isinstance(obj, QuerySet):
        return list(obj)
    elif isinstance(obj, Model):
        obj.__dict__.update({'unicode': obj.__unicode__()})
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
    elif isinstance(obj, FieldFile):
        return {
            'url': obj.url,
            'name': obj.name,
            'size': obj.size,
        }
    elif isinstance(obj, SorlImageFile):
        return {
            'key': obj.key,
            'ratio': obj.ratio,
            'url': obj.url,
            'name': obj.name,
            'size': obj.size,
        }
    elif isinstance(obj, forms.ModelForm) or isinstance(obj, forms.Form):
        _form = {
            'data': obj.data if hasattr(obj, 'data') else None,
        }
        if obj.errors:
            _form.update({'errors': obj.errors})
        return _form
    elif isinstance(obj, Promise):
        return unicode(obj)
    return obj


def render_to_json(content_type='application/json', is_mongo=False):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            dt = func(request, *args, **kwargs)
            response = make_http_response(content_type=content_type)
            encoder = partial(model_json_encoder, is_mongo=is_mongo)
            response.write(json.dumps(dt, default=encoder))
            return response
        return wrapper
    return decorator


# todo: refactor delete this dependence
def render_to(template, allow_xhr=False, content_type='text/html'):
    _content_type = content_type

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = make_http_response(content_type='application/json')
            dt = func(request, *args, **kwargs)
            if not isinstance(dt, dict):
                raise ImproperlyConfigured(
                    "render_to should take dict instance not %s" % type(dt))
            # overrides
            tmpl = get_skin_template(request.user, dt.get('_template',
                                                          template))

            ct = dt.get('_content_type', _content_type)

            force_ajax = (
                request.is_ajax() or request.META.get(
                    'HTTP_X_FORCE_XHTTPRESPONSE', None)
            )
            if 'redirect' in dt:
                if force_ajax:
                    response.write(json.dumps({"status": "ok"}))
                    return response

                args = dt.get('redirect-args', [])
                if args:
                    redr = reverse(dt['redirect'], args=args)
                    return redirect(redr)
                return redirect(dt['redirect'])

            if ct.lower() == 'text/html':
                if force_ajax and allow_xhr:
                    response.write(json.dumps(dt, default=model_json_encoder))
                    return response
                return render_to_response(
                    tmpl, dt, context_instance=RequestContext(request)
                )

            elif ct.lower() == 'text/csv':
                response = make_http_response(content_type=ct)
                response['Content-Disposition'] = \
                    'attachment; filename="export.csv"'
                response.write(
                    render_to_string(tmpl, dt)
                )
                return response

            elif ct.lower() in ('text/json', 'text/javascript',
                                'application/json'):
                response = HttpResponse()
                response['Content-Type'] = ct
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
    r = re.compile(r'\((?P<tag>\w+)\)\[(?P<text>.*?)\]', re.M | re.I | re.S)
    result = r.findall(string)
    html = ''
    for (tag, text) in result:
        if tag not in ('spoiler', 'off', 'video'):
            continue
        if tag == 'spoiler':
            html = render_to_string('core/s_comments.html',
                                    {'spoiler_text': text})
        elif tag == 'off':
            html = render_to_string('core/off_comments.html', {
                'offtopic_text': text})
        elif tag == 'video':
            ident = text[text.rindex('/') + 1:text.rindex('.')]
            ident = re.sub(r'\s+', '_', ident)
            html = render_to_string(
                'core/video_comments.html',
                {
                    'video_text': text,
                    'ident': ident
                }
            )
        html = re.sub(r'\n+', '', html)
        string = string.replace('(%s)[%s]' % (tag, text), html)
    # quote
    r = re.compile(
        r'\((?P<user>[\w\d\- ]+)\){(?P<quote>.*?)}',
        re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    result = r.findall(string)
    for (username, text) in result:
        if text:
            user = (
                get_object_or_None(settings.AUTH_USER_MODEL,
                                   nickname__iexact=username)
                or AnonymousUser()
            )
            html = render_to_string(
                'core/q_comments.html', {
                    'quote_user': user, 'quote_text': text}
            )
            html = re.sub(r'\n+', '', html)
            string = string.replace('(%s){%s}' % (username, text), html)
    string = string.replace('(cut)', '')
    return string


def unescape(string):
    string = string.replace('&lt;', '<')
    string = string.replace('&gt;', '>')
    return string


def render_filter(value, arg):
    #: todo resolve bb code
    def render_bbcode(source):
        return source

    syntaxes = [i[0] for i in settings.SYNTAX]
    if arg in syntaxes:
        if arg in 'bb-code':
            return unescape(value)
        elif arg in 'textile':
            return render_textile(value)
    return render_textile(value)
