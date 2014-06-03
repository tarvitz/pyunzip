# coding: utf-8
import importlib
from django.template import Library, Node

from django.contrib.auth import get_user_model
User = get_user_model()

from django.template import TemplateSyntaxError
from apps.core.helpers import get_content_type_or_None

register = Library()


# TODO: refactor it
class GetWarningNode(Node):
    def __init__(self, user, context_var):
        self.user = user
        self.context_var = context_var

    def render(self, context):
        user = self.user.resolve(context, ignore_failures=True)
        from apps.wh.models import Warning
        from django.db.models import Q
        kw = {}
        if hasattr(user, 'army'):
            if hasattr(user.army, 'side'):
                kw.update({'type__side': user.army.side})
        warnings = Warning.objects.filter(Q(user=user, **kw))
        if not warnings:
            warnings = Warning.objects.filter(user=user)
            if len(warnings):
                warning = warnings[0]
            else:
                return ''
        else:
            warning = warnings[0]
        context[self.context_var] = warning
        return ''


#{% get_warning for user as warn %}
def get_warning(parser, token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError("get_warning should take 4 arguments")
    if bits[1] != 'for':
        raise TemplateSyntaxError("second argument should be 'for'")
    if bits[3] != 'as':
        raise TemplateSyntaxError("second argument should be 'as'")
    user = parser.compile_filter(bits[2])
    context_var = bits[4]
    return GetWarningNode(user, context_var)
register.tag(get_warning)


class GetObjectMetaNode(Node):
    def __init__(self, var, varname=None):
        self.var = var
        self.varname = varname

    def render(self, context):
        var = self.var.resolve(context, ignore_failures=True)
        if self.varname:
            context[self.varname] = var._meta
        return var._meta if not self.varname else ''


@register.tag(name='get_object_meta')
def get_object_meta(parser, token):
    bits = token.contents.split()
    if len(bits) != 2 and len(bits) != 4:  # get_object_meta var as varname
        raise TemplateSyntaxError(
            "get_object_meta requires two or four arguments")
    if bits[2] != 'as':
        raise TemplateSyntaxError("third argument should be as")
    var = parser.compile_filter(bits[1])
    varname = None
    if len(bits) == 4:
        varname = bits[3]
    return GetObjectMetaNode(var, varname)


class GetObjectContentTypeNode(Node):
    def __init__(self, var, varname=None):
        self.var = var
        self.varname = varname

    def render(self, context):
        var = self.var.resolve(context, ignore_failures=True)
        meta = getattr(var, '_meta', {})

        obj = {
            'content_type': get_content_type_or_None(var),
            'id': var.pk,
            'app': meta.app_label,
            'model': meta.module_name,
        }

        if self.varname:
            context[self.varname] = obj
        return obj if not self.varname else ''


@register.tag(name='get_content_type')
def get_content_type(parser, token):
    bits = token.contents.split()
    if len(bits) != 2 and len(bits) != 4:  # get_object_meta var as varname
        raise TemplateSyntaxError(
            "get_content_type requires two or four arguments")
    if bits[2] != 'as':
        raise TemplateSyntaxError("third argument should be as")
    var = parser.compile_filter(bits[1])
    varname = None
    if len(bits) == 4:
        varname = bits[3]
    return GetObjectContentTypeNode(var, varname)


class GetFormNode(Node):
    def __init__(self, init, varname, use_request, instance=None):
        self.init = init[1:-1]
        self.varname = varname
        self.use_request = use_request
        self.instance = instance

    def render(self, context):
        instance = (
            self.instance.resolve(context, ignore_failures=True)
            if self.instance else None
        )
        app = self.init[:self.init.rindex('.')]
        _form = self.init[self.init.rindex('.')+1:]
        #module = __import__(app, 0, 0, -1)
        module = importlib.import_module(app)
        form_class = getattr(module, _form)
        context[self.varname] = (
            form_class(request=context['request'], instance=instance)
            if self.use_request else form_class(instance=instance)
        )
        return ''


@register.tag
def get_form(parser, tokens):
    bits = tokens.contents.split()
    # get_form 'apps.' for varname [use request]
    if 4 > len(bits) < 7:
        raise TemplateSyntaxError(
            "get_form 'app.model.Form' for form [use_request] instance")
    if bits[2] != 'as':
        raise TemplateSyntaxError("the second argument must be 'as'")
    init = bits[1]
    varname = bits[3]

    use_request = bits[4] if len(bits) > 4 else ""

    if 'no_request' in use_request:
        use_request = False

    instance = bool(bits[5] if len(bits) > 5 else None)
    if instance:
        instance = parser.compile_filter(bits[5])
    return GetFormNode(init, varname, use_request, instance)
