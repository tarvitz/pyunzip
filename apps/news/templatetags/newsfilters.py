# -*- coding: utf-8  -*-
import re
import six
from apps.thirdpaty.textile import render_textile

from django.template import Library
from django.conf import settings
from django.template.defaultfilters import striptags

register = Library()


@register.filter(name='newscut')
def newscut(value, arg):
    if len(six.text_type(value)) > int(arg):
        result = value[0:int(arg)] + " ..."
        return result
    return value


@register.filter(name='spfilter')
def spfilter_filter(value):
    _true = six.PY2 and 1 or True

    value = value.join('\n\n')
    result = value

    m = re.findall(r'\[url\]\S+\[/url\]', result)
    if m is not None:
        for l in m:
            link = "<a href='%s'>%s</a>" % (l[5:-6], l[5:-6])
            result = result.replace(l, link, 1)

    m = re.findall('\[code\][\w+ \S]+\[/code\]', result)
    if m is not None:
        for l in m:
            code = "<div id='code'>\n%s\n</div>" % (l[6:-7])
            result = result.replace(l, code, 1)
    while _true:
        m = re.search('\[url=(\S+)\](.*)\[/url\]', result)
        if m is not None:
            link = "<a href='%s'>%s</a>" % (m.group(1), m.group(2))
            result = result.replace(m.group(), link)
        else:
            break

    while _true:
        m = re.search(r'\[img id=(\S+)src=(\S+)\]', result)
        if m is not None:
            img = "<img id='%s' src='%s'>" % (m.group(1), m.group(2))
            result = result.replace(m.group(), img)
        else:
            break
    result = result.replace('[{', '[')
    result = result.replace('}]', ']')
    return result


@register.filter(name='spadvfilter')
def spadvfilter(value):
    result = spfilter_filter(value)
    for line in re.findall(
        "<a.[\w\S]*?.*?href=.javascript[\w\S]*?</a>", result
    ):
        result = result.replace(line, '')
    return result


@register.filter(name='spfilter2')
def spfilter2(value):
    _true = six.PY2 and 1 or True

    result = value.replace('\n', '<br>')
    result = result.replace('"', "&quot;")
    map_tag = ['b', 'i', 'u']
    for i in map_tag:
        result = result.replace('[%s]' % i, '<%s>' % i)
        result = result.replace('[/%s]' % i, '</%s>' % i)

    for link in re.findall(r'[^u^r^l].(http://\S+)', result):
        result = result.replace(link, "<a href='%s'>%s</a>" % (link, link), 1)

    m = re.findall(r'\[url\]\S+\[/url\]', result)
    if m is not None:
        for l in m:
            link = "<a href='%s'>%s</a>" % (l[5:-6], l[5:-6])
            result = result.replace(l, link, 1)

    while _true:
        # hmmm, it didn't work proper with o_O with re.findall(...)[0]
        m = re.search('\[url=(\S+)\](\S+)\[/url\]', result)
        replace_str = re.findall(r'\[url=\S+\]\S+\[/url\]', result)
        if replace_str:
            replace_str = replace_str[0]
        if m is not None:
            link = '<a href="%s">%s</a>' % (m.group(1), m.group(2))
            result = result.replace(replace_str, link, 1)
        else:
            break
    result = result.replace('[{', '[')
    result = result.replace('}]', ']')
    return result


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
        elif arg in 'markdown':
            return spadvfilter(striptags(value))
        return render_textile(value)
    return render_textile(value)
