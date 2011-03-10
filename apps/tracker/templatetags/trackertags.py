# coding: utf-8
from django.template import Library,Node,TemplateSyntaxError
from apps.tracker.models import SeenObject
from apps.core.helpers import get_content_type,get_object_or_none

register = Library()

class CheckForUpdates(Node):
    def __init__(self,obj,varname,user):
        self.object = obj
        self.varname = varname
        self.user = user

    def render(self,context):
        obj = self.object.resolve(context,ignore_failures=True)
        user = self.user.resolve(context,ignore_failures=True)
        if user.is_anonymous(): 
            context[self.varname] = False 
            return ''
        ct = get_content_type(obj) #breaks content_type retrieving 
        exists = get_object_or_none(SeenObject, content_type=ct, object_pk=obj.pk,user=user)   
        if exists:
            context[self.varname] = False
        else:
            context[self.varname] = True
        return ''

def check_for_updates(parser,tokens):
    bits = tokens.contents.split()
    if len(bits) != 4: #check_for_updates object varname user
        raise TemplateSyntaxError, "check_for_updates takes 3 arguments at least"
    obj = parser.compile_filter(bits[1])
    user = parser.compile_filter(bits[3])
    return CheckForUpdates(obj,bits[2],user)
check_for_updates = register.tag(check_for_updates)

