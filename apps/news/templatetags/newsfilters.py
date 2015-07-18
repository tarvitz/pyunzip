# -*- coding: utf-8  -*-
import re
import six
from apps.thirdpaty.textile import render_textile

from django.template import Library
from django.conf import settings
from django.template.defaultfilters import striptags

register = Library()


@register.filter(name='textile_filter')
def textile_filter(value):
    return render_textile(value)


@register.filter(name='render_filter')
def render_filter(value, arg):
    syntaxes = [i[0] for i in settings.SYNTAX]
    if arg in syntaxes:
        if arg in 'bb-code':
            return striptags(value)
        elif arg in 'textile':
            return render_textile(value)
        return render_textile(value)
    return render_textile(value)
