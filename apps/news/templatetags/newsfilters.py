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
    """
    renders only to textile

    :param str value: string for render
    :param str arg: syntax types (not important this time)
    :rtype: str
    :return: rendered string
    """
    return render_textile(value)
