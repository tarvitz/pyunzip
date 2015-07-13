# coding: utf-8
from apps.core.helpers import get_content_type, get_object_or_None
from apps.comments.models import CommentWatch

from django.template import Library, Node
from django.template import TemplateSyntaxError

register = Library()


class CommentWatchNode(Node):
    def __init__(self, obj, varname):
        self.obj = obj
        self.varname = varname

    def render(self, context):
        obj = self.obj.resolve(context, ignore_failures=True)
        if not obj:
            return ''
        ct = get_content_type(obj)
        user = (
            context['request'].user.is_authenticated()
            and context['request'].user
        )
        # get comment watch for current user
        comment_watch = get_object_or_None(CommentWatch, content_type=ct,
                                           object_pk=obj.pk,
                                           user=user,
                                           is_disabled=False)

        context[self.varname] = comment_watch
        return ''


@register.tag
def get_comment_watch(parser, tokens):
    """ {% get_comment_watch object as comment_watch_instance %}

    :param parser: parser
    :param tokens: tokens
    :return: CommentWatchNode
    """
    bits = tokens.contents.split()
    if len(bits) < 4:
        raise TemplateSyntaxError(
            "get_comment_watch object as comment_watch"
        )
    if bits[2] != 'as':
        raise TemplateSyntaxError("the second argument must be 'as'")
    obj, varname = bits[1], bits[3]
    obj = parser.compile_filter(obj)
    return CommentWatchNode(obj, varname)
