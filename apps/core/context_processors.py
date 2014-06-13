# coding: utf-8
from apps.wh.models import MiniQuote
from django.conf import settings


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
    return ({
        'base_template': template,
        'bootstrap_css_theme': 'css/bootstrap-{0}.css'.format(
            request.user.get_css_theme() or 'light')
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
