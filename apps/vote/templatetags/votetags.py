# ^^, coding: utf-8 ^^,
from django.template import Library, Node
from django.db.models import get_model
from django.template import TemplateSyntaxError
from apps.vote.models import Vote
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_content_type,get_template_or_none
from apps.vote.helpers import vote_stars_calculate as stars_calculate

register = Library()
class GetVotesForObject(Node):
    def __init__(self, obj, varname, stars=False):
        self.varname = varname
        self.obj = obj
        self.stars = stars
    def render(self, context):
        obj = self.obj.resolve(context, ignore_failures=True)
        #obsolete
        #model_name = object.__class__.__doc__.split('(')[0].lower()
        #ct = ContentType.objects.get(model=model_name)
        #TODO: fixit
        ct = get_content_type(obj)
        try:
            vote = Vote.objects.get(content_type=ct,object_pk=str(obj.pk))
            if self.stars:
                context[self.varname] = stars_calculate(float(vote.rating))
            else:    
                context[self.varname] = vote
            return ''
        except Vote.DoesNotExist:
            if self.stars: context[self.varname] = stars_calculate(0)
            else: context[self.varname] = 0
            return ''

def get_vote(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 5: #get_vote for object as vote
        raise TemplateSyntaxError, "get_vote takes exactly two arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "the second argument must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "the fourth argument must be 'as'"
    obj = parser.compile_filter(bits[2])
    return GetVotesForObject(obj,bits[4])
get_vote = register.tag(get_vote)

def get_vote_stars(parser, tokens):
    bits = tokens.contents.split()
    ## get_vote_stars for obj as stars
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_vote_stars takes exactly two arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "the second argument must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "the fourth argument must be 'as'"
    object = parser.compile_filter(bits[2])
    return GetVotesForObject(object,bits[4],True)
get_vote_stars = register.tag(get_vote_stars)

class GetUserVotedForObject(Node):
    def __init__(self, object,user, varname, stars=False):
        self.varname = varname
        self.object = object
        self.user = user
        self.stars = stars
    def render(self, context):
        object = self.object.resolve(context, ignore_failures=True)
        user = self.user.resolve(context, ignore_failures=True)
        #model_name = object.__class__.__doc__.split('(')[0].lower()
        #ct = ContentType.objects.get(model=model_name)
        ct = get_content_type(object)

        try:
            vote = Vote.objects.get(content_type=ct,object_pk=str(object.pk))
            voted = vote.users.filter(id=user.id)
            if voted:
                context[self.varname] = True
            else:
                context[self.varname] = False
            return ''
        except Vote.DoesNotExist:
            context[self.varname] = False
            return ''


def check_user_voted(parser, tokens):
    bits = tokens.contents.split()
    ## check_user_voted for vote with username as voted
    if len(bits) != 7:
        raise TemplateSyntaxError, "check_user_voted takes exactly two arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "the second argument must be 'for'"
    if bits[3] != 'with':
        raise TemplateSyntaxError, "the third argument must be 'with'"
    if bits[5] != 'as':
        raise TemplateSyntaxError, "the fourth argument must be 'as'"
    object = parser.compile_filter(bits[2])
    user = parser.compile_filter(bits[4])
    return GetUserVotedForObject(object,user,bits[6])
check_user_voted = register.tag(check_user_voted)

class DoBindObject(Node):
    def __init__(self, object,varname):
        self.varname = varname
        self.object = object
    def render(self, context):
        object = self.object.resolve(context, ignore_failures=True)
        context[self.varname] = object
        app_label = unicode(type(object)).split("'")[1]
        #improve this block
        app_label = app_label.split('.models')[0]
        try:
            app_label = app_label.split('.')[1]
        except:
            pass
        #sphinx fixtures
        if hasattr(object, '_sphinx') or hasattr(object, '_current_object'):
            obj = object._current_object.__class__.__name__.lower()
        else:
            obj = object.__class__.__name__.lower()
        values = {
            'model_name': obj,
            'app_label': app_label,
        }
        context['votes'] = values
        #return values
        return ''

def bind(parser,tokens):
    bits = tokens.contents.split()
    # bind r as object
    if len(bits) != 4:
        raise TemplateSyntaxError, "bind takes exactly two arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the third argument must be 'as'"
    object = parser.compile_filter(bits[1])
    return DoBindObject(object,bits[3])
bind = register.tag(bind)

class GetVoteObjectTemplate(Node):
    def __init__(self, object, varname):
        self.object = object
        self.varname = varname
    def render(self,context):
        object = self.object.resolve(context, ignore_failures=True)
        try:
            len(object)
            object = object[0]
        except TypeError:
            pass
        template = get_template_or_none("best_%s.html" % object.subclass_name,plain=True)
        context[self.varname] = template #best_replays.html best_images.html
        return ''

def get_best_object_template(parser,tokens):
    """ get_best_object_template for vote(s) as vote_template """
    bits = tokens.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_besst_object_template takes exactly two arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "the third argument should be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "the third argument should be 'as'"
    object = parser.compile_filter(bits[2])
    return GetVoteObjectTemplate(object,bits[4])

get_best_object_template = register.tag(get_best_object_template)
