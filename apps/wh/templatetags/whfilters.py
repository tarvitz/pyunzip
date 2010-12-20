# -^^- coding: utf-8  -^^-

from django.template import Library
from django import template
from django.utils.translation import ugettext_lazy as _

register = Library()

@register.filter(name='avatarcut')
def avatarcut(value):
	return value[value.index('/media'):]

@register.filter(name='mediacut')
def mediacut(value):
	if not value: return ''
	return value[value.index('/media'):]

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

#end OF DEPRECATED SECTION
