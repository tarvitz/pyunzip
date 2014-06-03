# coding: utf-8
from apps.wh.models import (PM, MiniQuote)

from django.conf import settings
from django.template.loader import get_template


def core(request):
    base = base_template(request)
    base.update(global_referer(request))
    base.update(global_settings(request))
    base.update({
        'miniquote': MiniQuote.objects.order_by('?')[0]
    })
    return base


def base_template(request):
    template = settings.DEFAULT_TEMPLATE
    is_auth = request.user.is_authenticated()
    skin_css_path = None
    if is_auth and request.user.skin:
        templ = "skins/%s/base.html" % (request.user.skin.name.lower())
        skin_css_path = "%(root)s/%(skin)s/main.css" % {
            'root': settings.STYLES_URL,
            'skin': request.user.skin.name.lower()
        }
        try:
            get_template(templ)
            template = templ
        except:
            pass
    return ({
        'base_template': template,
        'skin_css_path': skin_css_path
    })


def global_settings(request):
    from django.conf import settings
    return {
        'gs': settings,
        'global_settings': settings,
        'settings': {'document': settings.DOCUMENT}
    }


def global_referer(request):
    return {
        'global_referer': request.META.get('HTTP_REFERER','/'),
        'current_referer': request.META.get('PATH_INFO', '/')
    }
