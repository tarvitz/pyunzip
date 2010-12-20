#!/usr/bin/env python

import re
import sys
from django.template.loader import get_template

text = """

and the last one
{[color3] : #dd11dd}
fuck : #ff11ff}
test
{[<a href="http://source.com">source.com</a>] : #FF00FF}
{[color_test <a href="text">a</a>] : #FF00FF}

{c
{onemore thing : #color}
{c test or something ;) c}
{r what the fuck!? r}
{l left alignment l}
{c megatest }
c}
(spoiler)[a lot of ... text]
(spoiler)[a lot of text
....]
(spoiler)[
(quote)[ :)) quote ]
\]
(spoiler)[dasds \\]]
{c![test](/image/1) }
{c![test](/image/2) }
{c c}
"""

#links
def __markdown2_greed_alignment(text):
    map = ['r','l','j','c']
    for key in map:
        group = re.compile(r'\{(%s)(.*)%s\}' % (key,key), re.S|re.M)
        raw = re.compile(r'\{%s.*%s\}' % (key,key), re.S|re.M)
        while (':P'):
            replace_text = raw.findall(text)
            groups = group.findall(text)
            if not replace_text or not groups: break
            for i in replace_text:
                alignment, phrase = groups[replace_text.index(i)]
                if "r" in alignment: alignment = "right"
                if "l" in alignment: alignment = "left"
                if "c" in alignment: alignment = "center"
                if "j" in alignment: alignment = "justify"
                replacement = "<div align=\"%s\">%s</div>" % (alignment, phrase)
                text = text.replace(i, replacement)
    return text
def __markdown2_non_greed_alignment(text):
    group = re.compile(r'\{([r|l|c|j])(.*)\}', re.S|re.M)
    raw = re.compile(r'\{[r|l|c|j].*\}', re.S|re.M)
    while (':P'):
        replace_text = raw.findall(text)
        groups = group.findall(text)
        if not replace_text or not groups: break
        for i in replace_text:
            alignment, phrase = groups[replace_text.index(i)]
            if "r" in alignment: alignment = "right"
            if "l" in alignment: alignment = "left"
            if "c" in alignment: alignment = "center"
            if "j" in alignment: alignment = "justify"
            replacement = "<div align=\"%s\">%s</div>" % (alignment, phrase)
            text = text.replace(i, replacement)
    return text

def __markdown2_link_color(text):
    group = re.compile(r'\{\[(<a.*?>.*?</a>)\] : (.*?)\}', re.S|re.M)
    raw = re.compile(r'\{\[<a.*?>.*?</a>\] : .*?\}', re.S|re.M)
    replace_text = raw.findall(text)
    groups = group.findall(text)
    for i in replace_text:
        phrase, color = groups[replace_text.index(i)]
        replacement = phrase.replace('<a ','<a style="color: %s;" ' % color )
        text = text.replace(i, replacement)
    return text

def __markdown2_tags(text):
    #(tag)[content]
    for i in ('spoiler','quote',):
        raw = re.compile('\('+i+'\)\[.*?\]', re.S|re.M)
        group = re.compile('\(('+i+')\)\[(.*?)\]', re.S|re.M)
        replace_text = raw.findall(text)
        groups = group.findall(text)
        spoiler_count = 0
        for r in replace_text:
            tag, content = groups[replace_text.index(r)]
            if tag in 'quote':
                replacement = "<div id='%s'>%s</div>" % (tag, content)
            elif tag in 'spoiler':
                replacement = """
                <a href='#' onclick=\"show_hide('spoiler_%i');\">spoiler</a>
                <span style='display: none' class='%s' id='spoiler_%i'>
                %s
                </span>
                """ % (spoiler_count, tag,spoiler_count,content)
                #get_template = 'quotes.html'

                spoiler_count += 1
            else:
                replacement = "<span id='%s'>%s</span>" % (tag, content)
            text = text.replace(r, replacement)
    return text

#another blocks and so on
def markdown2_color(text):
    text = __markdown2_link_color(text)
    text = __markdown2_greed_alignment(text)
    text = __markdown2_non_greed_alignment(text)
    #text = __markdown2_tags(text)
    group = re.compile(r'\{\[(.*?)\] : (.*?)\}', re.S|re.M)
    raw = re.compile(r'\{\[.*?\] : .*?\}', re.S|re.M)
    replace_text = raw.findall(text)
    groups =  group.findall(text)
    for i in replace_text:
        phrase, color = groups[replace_text.index(i)]
        replacement = "<span style=\"color: %s\">%s</span>" % (color, phrase)
        text = text.replace(i, replacement)
    return text
        
#print markdown2_color(text)
