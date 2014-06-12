# coding: utf-8
from django.template import Library, Node
from django.template import TemplateSyntaxError

from apps.karma.models import Karma


register = Library()


class GetKarmaPowerForUser(Node):
    def __init__(self, user, varname):
        self.varname = varname
        self.user = user
        
    def render(self, context):
        user = self.user.resolve(context, ignore_failures=True)
        karma = Karma.objects.filter(user=user)
        if karma:
            karma = karma[0]
            context[self.varname] = karma.karma
        else:
            context[self.varname] = 0
        return ''


def get_karma_power(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 5:  # get_vote for object as vote
        raise TemplateSyntaxError(
            "get_karma_power takes exactly two arguments")
    if bits[1] != 'for':
        raise TemplateSyntaxError("the second argument must be 'for'")
    if bits[3] != 'as':
        raise TemplateSyntaxError("the fourth argument must be 'as'")
    user = parser.compile_filter(bits[2])
    return GetKarmaPowerForUser(user, bits[4])
get_karma_power = register.tag(get_karma_power)
