# -^^- coding: utf-8 -^^-
from django.template import Library
from django import template
from django.utils.translation import ugettext_lazy as _

import re

register = Library()

@register.filter(name='strcut')
def strcut(value,arg):
	if not value: return ''
	if len(value)>int(arg):
		result = value[0:int(arg)] + " ..."
		return result
	return value

class PagesNode(template.Node):	
	def __init__(self, pager, var_name):
		self.pager = pager
		self.var_name = var_name

	def render(self, context):
		pager_list = list()
		#for i in xrange(self.pager):
		#	pager_list.append(i)
		#context[self.var_name] = pages_list
		return ''
def do_get_pages_from(parser, token):
	try:
		#splitting by spaces
		tag_name, arg = token.contents.split(None,1)
	except ValueError:
		msg = '%r tag requires argument' % token.contents[0]
		raise template.TemplateSyntaxError(msg)
	
	m = re.search(r'(.*?) as (\w+)', arg)
	if m:
		fmt, var_name = m.groups()
		print fmt
	else:
		msg = '%r tag had invalid arguments' % tag_name
		raise template.TemplateSyntaxError(msg)

	return PagesNode(fmt, var_name)

#register.tag('get_pages_from', do_get_pages_from)
