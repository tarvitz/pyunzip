# -^^- coding: utf-8  -^^-

from django.template import Library
from django import template
from django.utils.translation import ugettext_lazy as _

try:
	from apps.thirdpaty.markdown2 import markdown
except ImportError:
	#making a hint
	def markdown(value):
		return value
from apps.helpers.markdown2_wrapper import markdown2_color
from apps.thirdpaty.postmarkup import render_bbcode
from apps.thirdpaty.creole.shortcuts import creole_filter as render_creole
from apps.thirdpaty.textile import render_textile
from django.conf import settings
from django.template.defaultfilters import striptags
import re

register = Library()

@register.filter(name='newscut')
def newscut(value,arg):
	if len(unicode(value))>int(arg): 
		result = value[0:int(arg)] + " ..."
		return result
	return value
@register.filter(name='spfilter')
def spfilter(value):
	value = value.join('\n\n') #markdown fixes
	result = markdown(value)
	result = markdown2_color(result) #makin' a wrapper for colors and link colors :)

        m = re.findall(r'\[url\]\S+\[/url\]',result)
        if m is not None:
                for l in m:
                        link = "<a href='%s'>%s</a>" % (l[5:-6],l[5:-6])
                        result = result.replace(l,link,1)
        #s = "[url=http://somelocation]somelocation[/url]"
        m = re.findall('\[code\][\w+ \S]+\[/code\]', result)
        if m is not None:
                for l in m:
                        code = "<div id='code'>\n%s\n</div>" % (l[6:-7])
                        result = result.replace(l,code,1)
	while (':P'):
                #unsafe o_O"
		#m = re.search('\[url=(\S+)\]([\W\s\d ]+)\[/url\]',result)
		m = re.search('\[url=(\S+)\](.*)\[/url\]',result)
                if m is not None:
                        link="<a href='%s'>%s</a>" % (m.group(1), m.group(2))
                        result = result.replace(m.group(),link)
                else:
                        break
	while (':P'):
                m = re.search('\[img id=(\S+)\ src=(\S+)\]',result)
                if m is not None:
                        img="<img id='%s' src='%s'>" % (m.group(1), m.group(2))
                        result = result.replace(m.group(),img)
                else:
                        break
	result = result.replace('[{','[')
	result = result.replace('}]',']')
	return result
@register.filter(name='spadvfilter')
def spadvfilter(value):
	result = spfilter(value)
	#making unsafe more safty
	for line in re.findall("<a.[\w\S]*?.*?href=.javascript[\w\S]*?</a>", result):
		result = result.replace(line,'')
	return result

@register.filter(name='spfilter2')
def spfilter2(value):
	result = value.replace('\n','<br>')
	result = result.replace('"', "&quot;")
	map_tag = ['b','i','u']
	for i in map_tag:
		result = result.replace('[%s]' % i,'<%s>' % (i))
		result = result.replace('[/%s]' % i ,'</%s>' % (i))

	for link in re.findall('[^u^r^l].(http://\S+)',result):
		result = result.replace(link,"<a href='%s'>%s</a>" % (link,link),1)
	
	m = re.findall(r'\[url\]\S+\[/url\]',result)
	if m is not None:
		for l in m:
			link = "<a href='%s'>%s</a>" % (l[5:-6],l[5:-6])
			result = result.replace(l,link,1)
	#s = "[url=http://somelocation]somelocation[/url]"
	while (':P'):
		m = re.search('\[url=(\S+)\](\S+)\[/url\]', result)
		replace_str = re.findall(r'\[url=\S+\]\S+\[/url\]',result) #hmmm, it didn't work proper with o_O with re.findall(...)[0]
		if replace_str: replace_str = replace_str[0]
		if m is not None:
			link='<a href="%s">%s</a>' % (m.group(1), m.group(2))
			result = result.replace(replace_str,link,1)
		else:
			break
		#'<a href=%s>%s</a>' % (m.group(1), m.group(2))
	#result = result.replace('[url=]','<a href="')
	#result = result.replace('[/url]','"></a>')
	#result = result.replace('[b]','<b>')
	#result = result.replace('[/b]','</b>')
	#result = result.replace('[i]','</i>')
	#result = result.replace('[/i]','</i>')
	#result = result.replace('[u]', '[/u]')
	#result = result.replace('[/u]','[/u]')
	#avoid collisions put this last
	result = result.replace('[{','[')
	result = result.replace('}]',']')
	return result

@register.filter(name='bbfilter')
def bbfilter(value):
    return render_bbcode(value)

@register.filter(name='creole_filter')
def creole_filter(value):
    return render_creole(value)

@register.filter(name='textile_filter')
def textile_filter(value):
    return render_textile(value)

#takes syntax as arg
@register.filter(name='render_filter')
def render_filter(value,arg):
    #TODO: FIXME: fix this issue
    #if arg == '': #could be None obj passed
    #    return ''
    syntaxes = [i[0] for i in settings.SYNTAX]
    if arg in syntaxes:
        #how we could render ?
        if arg in 'bb-code':
            return striptags(render_bbcode(value))
        elif arg in 'creole' or arg in 'wiki':
            return striptags(creole_filter(value))
        elif arg in 'textile':
            return render_textile(value)
        elif arg in 'markdown':
            return striptags(spadvfilter(value))
        return render_textile(value)
        #default filter
        #return spadvfilter(value)
    else:
        return render_textile(value)
        #spadvfilter(value) #markdown by default

    
