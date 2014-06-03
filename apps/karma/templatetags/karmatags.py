# ^^, coding: utf-8 ^^,
from django.template import Library, Node
from django.template import TemplateSyntaxError
from apps.karma.models import Karma,KarmaStatus

from apps.core.helpers import get_settings
from django.db.models import Q

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
    if len(bits) != 5: #get_vote for object as vote
        raise TemplateSyntaxError, "get_karma_power takes exactly two arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "the second argument must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "the fourth argument must be 'as'"
    user = parser.compile_filter(bits[2])
    return GetKarmaPowerForUser(user,bits[4])
get_karma_power = register.tag(get_karma_power)

class GetKarmaStatus(Node):
    def __init__(self,current_user,user,varname):
        self.user = user
        self.varname = varname
        self.current_user = current_user

    def render(self,context):
        user = self.user.resolve(context,ignore_failures=True)
        current_user = self.current_user.resolve(context,ignore_failures=True)
        karma = Karma.objects.filter(user=user)
        is_humor = get_settings(current_user,'karma_humor',True)
        if karma:
            karma = karma[0]
            try:
                if is_humor:
                    #positive and negative karma divides the way of SQL query
                    if int(karma.karma_value)>0:
                        status = KarmaStatus.objects.order_by('-value','is_humor').filter(
                            Q(side=user.army.side)|Q(is_general=True),
                            value__lte=int(karma.karma_value))
                    else:
                        status = KarmaStatus.objects.order_by('value','is_humor').filter(
                            Q(side=user.army.side)|Q(is_general=True),
                            value__gte=int(karma.karma_value))

                else:
                    if int(karma.karma_value)>0:
                        status = KarmaStatus.objects.order_by('-value').exclude(
                            is_humor=True).filter(Q(side=user.army.side)|Q(is_general=True),
                            value__lte=int(karma.karma_value))
                    else:
                        status = KarmaStatus.objects.order_by('value').exclude(
                            is_humor=True).filter(Q(side=user.army.side)|Q(is_general=True),
                            value__gte=int(karma.karma_value))
                if status:
                    status = status[0]
                else:
                    pass
            except KarmaStatus.DoesNotExist:
                status = None
            context[self.varname] = status
        else:
            pass
        return ''

def get_karma_status(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 7: #get_karma_status with current_user for user as karma_status
        raise TemplateSyntaxError, "get_karma_status takes exactly two arguments"
    if bits[1] != 'with':
        raise TemplateSyntaxError, "the second argument must be 'with'"
    if bits[3] != 'for':
        raise TemplateSyntaxError, "the second argument must be 'for'"
    if bits[5] != 'as':
        raise TemplateSyntaxError, "the fourth argument must be 'as'"
    current_user = parser.compile_filter(bits[2])
    user = parser.compile_filter(bits[4])
    return GetKarmaStatus(current_user,user,bits[6])
get_karma_status = register.tag(get_karma_status)

