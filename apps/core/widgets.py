# input your code here :)
# coding: utf-8
#

from django.forms import Widget
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.forms.util import flatatt
from django.template.loader import get_template
from django.template import Context

class TinyMkWidget(Widget):
    # 
    def __init__(self,attrs=None):
        default_attrs = {'cols': '40', 'rows': '25'}
        if attrs:
            default_attrs.update(attrs)
        super(TinyMkWidget,self).__init__(default_attrs)

    def render(self,name,value,attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        tinymk_template = get_template('tinymk_widget.html')
        out = tinymk_template.render(Context({'tinymk':final_attrs}))
        out = out+mark_safe(u'<textarea%s>%s</textarea>' % (flatatt(final_attrs),
            conditional_escape(force_unicode(value))))
        return out
