# -^^- coding: utf-8  -^^-
""" Default warmist filters """

from django.template import Library
from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template,TemplateDoesNotExist
import os
from django.conf import settings

register = Library()
@register.filter(name='bool_list')
def bool_list(value,arg):
    if not value:
        return False
    if value[arg-1]:
        return True

@register.filter(name='lookup')
def lookup(value,arg):
    if arg in [i for i in value]:
        return True
    else:
        return False

@register.filter(name='list_gte')
def list_gte(value,arg):
    if not value: return False
    count = len(value)
    if int(count)>int(arg): return True
    return False

@register.filter(name='gt')
def gt(value,arg):
    if not value: return False
    if int(value)>int(arg):
        return True
    else:
        return False

@register.filter(name='gte')
def gte(value,arg):
    if not value: return True # Null, None is 0 too ;)
    if int(value)>=int(arg):
        return True
    else:
        return False

@register.filter(name='mod2')
def mod2(value):
    if not value: return 1
    return int(value)%2

@register.filter(name='avatarcut')
def avatarcut(value):
    if not value: return ''
    return value[value.index('/media'):]

@register.filter(name='mediacut')
def mediacut(value):
    if not value: return ''
    return value[value.index('/media'):]

@register.filter(name='namemediacut')
def namemediacut(value):
    if not value: return ''
    return value[value.rindex('/')+1:]

@register.filter(name='add_js')
def add_js(value,arg):
    value_str = str(value)
    return value_str.replace('<select ','<select %s ' % (arg))

@register.filter(name='gender_transform')
def gender_transform(value):
    if value == str('n'): return _('Not Identified')
    if value == str('m'): return _('Male')
    return _('Female')

#avatar army size cut, used for css
@register.filter(name='aacut')
def aacut(value):
    result = int(value)
    return result-result*0.2; #-20%

@register.filter(name='testfl')
def testfl(value):
    return value.lower()

@register.filter(name='getskin')
def getskin(value,arg=None):
    if value:
        if not arg:
            return ''
        path = "skins/%s/%s" % (value.lower(),arg)
        try:
            get_template(path)
            return path
        except TemplateDoesNotExist:
            return arg
        return path
    elif not value:
        if arg:
            return arg
        else:
            return ''
    if arg:
        return arg
    else:
        return ''
@register.filter(name='getskincss')
def getskincss(value,arg=None):
    if not arg:
        return ''
    if value:
        path = "%s/%s" % (value.lower(),arg)
        try:
            p = os.path.join(settings.STYLES_ROOT,path)
            os.stat(p)
            return path
        except:
            return arg
    else:
        return arg

@register.filter(name='or')
def or_filter(value,arg=None):
    if not value:
        if arg:
            return arg
        else: return ''
    else:
        return value
