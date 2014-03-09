# ^^, coding: utf-8 ^^,
import importlib
from django.template import Library, Node
from apps.news.models import News
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.wh.models import GuestActivity
from django.db.models import get_model
from django.template import TemplateSyntaxError
from apps.files.models import Replay,Image,Version
from apps.core.models import Settings
from django.template.defaultfilters import striptags
import re
from apps.core import get_skin_template
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AnonymousUser
from apps.news.templatetags.newsfilters import spadvfilter

from apps.core.helpers import get_settings, get_content_type_or_None

register = Library()
#returns 5 last news (:
class LastNewsNode(Node):
    def render(self, context):
        context['last_news'] = News.objects.all()[:5]
        return ''
def get_lastest_news(parser, token):
    return LastNewsNode()
get_lastest_news = register.tag(get_lastest_news)

class LastNewsNode2(Node):
    def __init__(self, num):
        self.num = num
    
    def render(self, context):
        context['last_news'] = News.objects.all()[:self.num]
        return ''
def get_lastest_news2(parset, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "get_lastest_news2 tag takes exactly one argument "
    return LastNewsNode2(bits[1]) #__init__(self, num)
get_lastest_news2 = register.tag(get_lastest_news2)

class LastNewsNode3(Node):
    def __init__(self, num, varname):
        self.num = num
        self.varname = varname
    
    def render(self, context):
        context[self.varname] = News.objects.all()[:self.num]
        return ''

def get_lastest_news3(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError, "get_lastest_news3 tag takes exactly three arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to the get_lastest_news3 tag must be 'as'"
    return LastNewsNode3(bits[1],bits[3])
get_lastest_news3 = register.tag(get_lastest_news3)

class LastOfSmthNode(Node):
    def __init__(self,model, num, varname):
        self.num, self.varname = num, varname
        self.model = get_model(*model.split('.'))
    
    def render(self, context):
        context[self.varname] = self.model._default_manager.all()[:self.num]
        return ''

def get_last_of_smth(parser, token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_last_of_smth tag takes exactly four argument"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "third argument to get_last_of_smth must be 'as'"
    return LastOfSmthNode(bits[1], bits[2], bits[4])
get_last_of_smth = register.tag(get_last_of_smth)

class CheckIfOnline(Node):
    def __init__(self, user,varname='user_is_online', minutes=15,is_return=False):
        self.varname = varname
        self.user = user
        self.minutes = minutes
        self.is_return = is_return

    def render(self, context):
        #getting the real object instead of string
        user = self.user.resolve(context,ignore_failures=True) #making from context real user-object
        import datetime as dt
        time = dt.datetime.now()-dt.timedelta(minutes=int(self.minutes))
        if not hasattr(user,'useractivity'):
            context[self.varname] = False
            if self.is_return: return 'offline'
            else: return ''
        if user.useractivity.is_logout:
            context[self.varname] = False
            if self.is_return: return 'offline'
            else: return ''
        if user.useractivity.activity_date > time:
            context[self.varname] = True
            if self.is_return: return 'online'
        else:
            context[self.varname] = False
            if self.is_return: return 'offline'
            else: return ''
        if self.is_return: return 'offline'
        else: return ''

def check_if_online(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) != 5: #check_if_online user as is_online 15
        raise TemplateSyntaxError, "check_if_online takes exactly three arguments"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the third argument must be 'as'"
    user = parser.compile_filter(bits[1]) #compile into ""context user-object"" instead of unicode string
    return CheckIfOnline(user, bits[3], bits[4])
check_if_online = register.tag(check_if_online)

def get_online(parser,tokens):
    bits = tokens.contents.split()
    if len(bits) != 2: #get_online user
        raise TemplateSyntaxError, "get_online takes exactly one argument"
    user = parser.compile_filter(bits[1])
    return CheckIfOnline(user,is_return=True)
get_online = register.tag(get_online)

class GetOnlineUsers(Node):
    def __init__(self,varname,offset_value):
        self.offset_value = offset_value
        self.varname = varname #varname to set the output
    def render(self,context):
        import datetime as dt
        time=dt.datetime.now()-dt.timedelta(minutes=int(self.offset_value))
        users = User.objects.filter(is_active=True,useractivity__is_logout=False,\
            useractivity__activity_date__gte=time)
        final_users = list()
        for n in xrange(0,len(users)):
            if users[n].settings:
                if users[n].settings.has_key('invisible'):
                    if not users[n].settings['invisible']:
                        final_users.append(users[n])
                else:
                    final_users.append(users[n])
        context[self.varname] = final_users

        return ''

def get_online_users(parser, token):
    bits = token.contents.split()
    if len(bits) != 4: #get_online_users as online_users 15
        raise TemplateSyntaxError, "get_online_users takes exactly two arguments"
    if bits[1] != 'as':
        raise TemplateSyntaxError, 'get_online_users second argument must be "as"'
    return GetOnlineUsers(bits[2], bits[3])
get_online_users = register.tag(get_online_users)

class GetOnlineGuests(Node):
    def __init__(self, varname, minutes):
        self.minutes = minutes
        self.varname = varname

    def render(self, context):
        import datetime as dt
        time = dt.datetime.now() - dt.timedelta(minutes=int(self.minutes))
        guests = GuestActivity.objects.filter(activity_date__gte=time).count()
        context[self.varname] = guests
        return ''

def get_guests_count(parser, token):
    bits = token.contents.split()
    if len(bits) != 4: #get_guests_count as guest_count 15
        raise TemplateSyntaxError, "get_guests_count takes exactly two arguments"
    if bits[1] != 'as':
        raise TemplateSyntaxError, "get_guests_count second argument must be 'as'"
    return GetOnlineGuests(bits[2], bits[3])
get_guests_count = register.tag(get_guests_count)

class UnreadNode(Node):
    def __init__(self, model, varname):
        self.model,self.varname = model,varname
        self.model = get_model(*model.split('.'))
    def render(self, context):
        context[self.varname] = self.model._default_manager.filter(approved=False).count()
        return ''

def get_unread(parser, token):
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError, "get_unread tag tages exactly four argument"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "third argument to get_unread must be as"
    return UnreadNode(bits[1], bits[3]) #get_unread app.model as var
get_unread = register.tag(get_unread)

class ImagesCountNode(Node):
    def __init__(self, model, varname):
        self.varname = varname
        self.model = model
    def render(self, context):
        obj = self.model.resolve(context, ignore_failures=True)
        count = Image.objects.filter(gallery=obj).count() 
        context[self.varname] = count
        return ''
    
def get_images_count(parser, token):
    bits = token.contents.split() #get_images_count for gallery as varname
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_images_count takes exactly four argument"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "Second argument to get_images_count must be for"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "Four argument to get_images_count must be as"
    obj = parser.compile_filter(bits[2])
    return ImagesCountNode(obj,bits[4])
get_images_count = register.tag(get_images_count)


class GetVersionsForGameNode(Node):
    def __init__(self, game, varname):
        self.game = game
        self.varname = varname

    def render(self,context):
        game = self.game.resolve(context, ignore_failures=True)
        versions = Version.objects.filter(game__exact=game).order_by(
            '-release_number').distinct('name').values('name')
        context[self.varname] = versions
        return ''

def get_versions_for_game(parser, token):
    bits = token.contents.split()
    if len(bits) != 5: # {% get_versions_for_game for game as versions %}
        raise TemplateSyntaxError, "get_versions_for_game tag takes exactly 4 arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "fourth argument to get_version_for_game must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "fourth argument to get_version_for_game must be 'as'"
    obj = parser.compile_filter(bits[2])
    return GetVersionsForGameNode(obj, bits[4])
get_versions_for_game = register.tag(get_versions_for_game)

class GetAuthorReplaysCountNode(Node):
    def __init__(self,user,context_var):
        self.user = user
        self.varname = context_var

    def render(self,context):
        user = self.user.resolve(context,ignore_failures=True)
        count = Replay.objects.filter(author=user).count()
        context[self.varname] = count
        return ''

def get_author_replays_count(parser,token):
    bits = token.contents.split()
    if len(bits) != 5: #get_author_replays_count for author as rep_count
        raise TemplateSyntaxError, "get_author_replays_count tag takes exactly 4 arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "fourth argument to get_version_for_game must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "fourth argument to get_version_for_game must be 'as'"
    user = parser.compile_filter(bits[2])
    return GetAuthorReplaysCountNode(user,bits[4])
get_author_replays_count = register.tag(get_author_replays_count)

class GetReplaysCountForVersionNode(Node):
    def __init__(self, game,varname,version='',type='all',patchlevel=''):
        self.game = game
        self.version = version
        self.varname = varname
        self.type = type
        self.patchlevel = patchlevel

    def render(self, context):
        game = self.game.resolve(context, ignore_failures=True)
        if self.version:
            version = self.version.resolve(context, ignore_failures=True)
        if self.patchlevel:
            patchlevel = self.patchlevel.resolve(context, ignore_failures=True)
        else:
            patchlevel = None
        if self.type == 'duel':
            if patchlevel:
                replays = Replay.objects.filter(type='1',version__game__exact=game,
                    version__name__iexact=version,
                    version__patch__exact=patchlevel).count()
            else:   
                replays = Replay.objects.filter(type='1',version__game__exact=game,
                    version__name__iexact=version).count()
        elif self.type == 'nonstd':
            if patchlevel:
                replays = Replay.objects.filter(type='0',version__game__exact=game,
                    version__name__iexact=version,
                    version__patch__exact=patchlevel).count()
            else:
                replays = Replay.objects.filter(type='0',
                    version__name__iexact=version).count()
        elif self.type == 'team':
            if patchlevel:
                replays = Replay.objects.exclude(type='0').exclude(type='1').filter(
                    version__game__exact=game,
                    version__name__iexact=version,
                    version__patch__exact=patchlevel).count()
            else:
                replays = Replay.objects.exclude(type='0').exclude(type='1').filter(
                    version__game__exact=game,
                    version__name__iexact=version).count()
        else:
            if patchlevel:
                replays = Replay.objects.filter(version__name__iexact=version,
                    version__game__exact=game,
                    version__patch=patchlevel).count()
            else:
                replays = Replay.objects.filter(version__game__exact=game,
                version__name__iexact=version).count()
        context[self.varname] = replays
        return ''

def get_replays_count_for_version(parser,token):
    #get_replays_count_for_version for game as _counts_ type all version_name version 1.0
    bits = token.contents.split()
    if bits[1] != 'for':
        raise TemplateSyntaxError, "second argument to get_replays_count_for_version must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "fourth argument to get_replays_count_for_version must be 'as'"
    if bits[5] != 'type':
        raise TemplateSyntaxError, "sixth argument to get_replays_count_for_version must by 'type'"
    obj = parser.compile_filter(bits[2])
    if len(bits) < 5:
        raise TemplateSyntaxError, "get_replays_count_for_version takes at least 4 arguments"
    elif len(bits) == 7:
        return GetReplaysCountForVersionNode(game=obj,varname=bits[4],type=bits[6])
    elif len(bits) == 8:
        version_name = parser.compile_filter(bits[7])
        return GetReplaysCountForVersionNode(game=obj,varname=bits[4],version=version_name,type=bits[6])
    elif len(bits) == 10:
        version_name = parser.compile_filter(bits[7])
        patch_level = parser.compile_filter(bits[9])
        return GetReplaysCountForVersionNode(game=obj,varname=bits[4],version=version_name,
            patchlevel=patch_level,type=bits[6])

get_replays_count_for_version = register.tag(get_replays_count_for_version)

class GetPatchLevelsNode(Node):
    def __init__(self, version, varname):
        self.version = version
        self.varname = varname
    def render(self, context):
        version = self.version.resolve(context, ignore_failures=True)
        patch_levels = Version.objects.filter(name__iexact=version).distinct('patch').values(
            'patch').order_by('-patch')
        context[self.varname] = patch_levels
        return ''
def get_patch_levels(parser,token):
    bits = token.contents.split()
    if len(bits) != 5: # {% get_patch_levels_for_version for _version_ as patchlevels %}
        raise TemplateSyntaxError, "get_patch_levels tag takes exactly 4 arguments"
    if bits[1] != 'for':
        raise TemplateSyntaxError, "second argument to get_patch_levels must be 'for'"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "fourth argument to get_patch_levels must be 'as'"
    obj = parser.compile_filter(bits[2])
    return GetPatchLevelsNode(obj, bits[4])
get_patch_levels = register.tag(get_patch_levels)

class NumberOfReplaysNode(Node):
    def __init__(self, model, varname):
        self.varname = varname
        #self.model = get_model(*model.split('.'))
        self.model = model
    def render(self, context):
        obj = self.model.resolve(context, ignore_failures=True)
        #we don't need anything to resolve dynamic as comments system does
        #therefore we use shortcut, besides we're tooooo lazy to get everything as common use
        all_replays = Replay.objects.filter(version__game__short_name__exact=obj.short_name).count()
        duels = Replay.objects.filter(type='1', version__game__short_name__exact=obj.short_name).count()
        teams = Replay.objects.exclude(type='1').filter(version__game__short_name__exact=obj.short_name).exclude(type='0').count()
        nonstds = Replay.objects.filter(type='0', version__game__short_name=obj.short_name).count()
        stats = { 'all': all_replays,
            'duels': duels,
            'teams': teams,
            'nonstds': nonstds,
            'game_name': obj.short_name
        }
        context[self.varname] = stats
        return ''

def get_replays_count(parser, token):
    bits = token.contents.split()
    if len(bits) != 5: # {% get_replays_count for _replay_ as rcount %}
        raise TemplateSyntaxError, "get_replays_count tag takes exactly 4 arguments"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "fourth argument to get_replays_count must be 'as'"
    obj = parser.compile_filter(bits[2])
    return NumberOfReplaysNode(obj, bits[4])
register.tag(get_replays_count)

#sounds horrible ;)
class GetUserFromNicknameNode(Node):
    def __init__(self,nick,varname=None,profile=False):
        self.nickname = nick
        self.varname = varname
        self.profile = profile
    def render(self,context):
        if self.profile:
            try:
                nickname = self.nickname.resolve(context,ignore_failures=True)
                user = User.objects.get(nickname__iexact=nickname)
                return user
            except User.DoesNotExist:
                raise TemplateSyntaxError,"Such 'nickname' does not exist"
            context[self.varname] = varname
            return ''
        else:
            try:
                user = self.nickname.resolve(context,ignore_failures=True)
                user = User.objects.get(nickname__iexact=user)
            except:
                return self.nickname.resolve(context,ignore_failures=True)
            style,css_class,css_id = None,None,None
            try:
                for rank in user.ranks.order_by('type__magnitude'):
                    if rank.get_style():
                        style = rank.get_style()
                    if rank.get_css_class(): css_class = rank.get_css_class()
                    if rank.get_css_id(): css_id = rank.get_css_id()
                    if style or css_class or css_id: break
                aggregate = ''
                if style:
                    aggregate = "style='%s' " % style
                if css_id: aggregate += "id='%s' " % css_id
                if css_class: aggregate += "class='%s'" % css_class
                if aggregate:
                    return "<span %s>%s</span>" % (aggregate, user.nickname)
                else:
                    return user.nickname
            except:
                raise TemplateSyntaxError,"You have passed wrong context variable as 'user' object "

#get_profile_by_nickname 'Saul Tarvitz' as _profile_
def get_profile_by_nickname(parser,token):
    bits = token.split_contents()
    if len(bits) !=4: 
        raise TemplateSyntaxError, "get_profile_by_nickname tag takes 3 argument"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "get_profile_by_nickname second argument must be 'as'"
    user = parser.compile_filter(bits[1])
    return GetUserFromNicknameNode(user,profile=True)
register.tag(get_profile_by_nickname)

def get_raw_nickname(parser,token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError, "get_raw_nickname tag takes 1 argument"
    user = parser.compile_filter(bits[1])
    return GetUserFromNicknameNode(user)
register.tag(get_raw_nickname)

class MarkdownPlusNode(Node): 
    def __init__(self,nodelist):
        self.nodelist = nodelist
    def __repr__(self):
        return "<MarkdownitNode>"
    def render(self,context):
        nodelist = self.nodelist.render(context)
        #replace text below as one code-block
        #(Nickname){Quote text}
        r = re.compile(r'\((?P<nick>[\w\s]+)\)\{(?P<quote>.*?)\}',re.I|re.L|re.S)
        f = re.compile(r'\([\w\s]+\)\{.*?\}',re.I|re.L|re.S)
        replace_text = r.findall(nodelist)
        raw_text = f.findall(nodelist)
        for i in replace_text:
            nickname,quote = i
            #alter markdownit with user skin capabillities
            quote_template = get_template('q_comments.html')
            try:
                user = User.objects.get(nickname__iexact=nickname)
                context['quote_user'] = user
            #if there is not a user what shall we done?
            except User.DoesNotExist:
                user = AnonymousUser()
                context['quote_user'] = user
            context['quote_text'] = quote
            html = quote_template.render(context)
            nodelist = nodelist.replace(raw_text[replace_text.index(i)],html)
        
        #(spoiler)[spoiler text here]
        r = re.compile(r'\((?P<spoil_marker>spoiler)\)\[(?P<spoil_text>.*?)\]',re.S|re.M|re.I)
        f = re.compile(r'\(spoiler\)\[.*?\]',re.S|re.M|re.I)
        spoiler_count = 0
        replace_text = r.findall(nodelist)
        raw_text = f.findall(nodelist)
        for i in replace_text:
            spoil_mark,spoiler_text = i
            spoiler_template = get_template('s_comments.html')
            context['spoiler_count'] = spoiler_count
            spoiler_count += 1
            context['spoiler_text'] = spoiler_text
            html = spoiler_template.render(context)
            nodelist = nodelist.replace(raw_text[replace_text.index(i)],html)
        #offtopic
        r = re.compile(r'\((?P<offtopic_marker>off)\)\[(?P<off_text>.*?)\]',re.S|re.M|re.I)
        f = re.compile(r'\(off\)\[.*?\]',re.S|re.M|re.I)
        replace_text = r.findall(nodelist)
        raw_text = f.findall(nodelist)
        for i in replace_text:
            offtopic_mark,offtopic_text = i
            offtopic_template = get_template('off_comments.html')
            context['offtopic_text'] = offtopic_text
            html = offtopic_template.render(context)
            nodelist = nodelist.replace(raw_text[replace_text.index(i)],html)

        out = mark_safe(nodelist)
        return out

def do_markdown_it(parser,token):
    nodelist = parser.parse(('endmarkdownit',))
    parser.delete_first_token()
    return MarkdownPlusNode(nodelist)
register.tag('markdownit',do_markdown_it)

class GetNicknameNode(Node):
    def __init__(self, model):
        self.model = model

    def render(self,context):
        user = self.model.resolve(context, ignore_failures=True)
        
        #if user.get_nickname:
        #    #implement here colorizing of the nicknames
        #    return user.get_nickname
        #else:
        #    #colorizing :)
        #    return user.nickname
        #   colorizing
        style,css_class,css_id = None,None,None
        try:
            for rank in user.ranks.order_by('type__magnitude'):
                #style, css_class, css_id = None,None,None
                if rank.get_style():
                    style = rank.get_style()
                if rank.get_css_class():
                    css_class = rank.get_css_class()
                if rank.get_css_id():
                    css_id = rank.get_css_id()
                if style or css_class or css_id: 
                    #print "break"
                    break
            aggregate = ''
            if style: aggregate = "style='%s' " % style
            if css_class: aggregate += "class='%s' " % css_class
            if css_id: aggregate += "id='%s'" % css_id
            
            if aggregate: 
                return "<span %s>%s</span>" % (aggregate, user.nickname)
            else:
                return user.nickname
        except:
            raise TemplateSyntaxError,"You have passed wrong context variable as 'user' object "
#merge with get_raw_nickname
def get_nickname(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "get_nickname tag takes 1 argument"
    user = parser.compile_filter(bits[1])
    return GetNicknameNode(user)

register.tag(get_nickname)


class GetSettingsNode(Node):
    def __init__(self, user, settings, context_var):
        self.user = user
        self.settings = settings
        self.context_var = context_var

    def render(self,context):
        user = self.user.resolve(context, ignore_failures=True)
        try:
            u_settings = Settings.objects.get(user=user)
        except Settings.DoesNotExist:
            context[self.context_var] = False
            return ''
        if self.settings in u_settings.get_decoded():
            context[self.context_var] = u_settings.get_decoded()[self.settings]
        else:
            context[self.context_var] = False
        return ''

#{% check_settings for user with some_settings as context_var %} returns True or False
def _get_settings(parser, token):
    bits = token.contents.split()
    if len(bits) != 7:
        raise TemplateSyntaxError, "check_settings tag takes 6 argument"
    if bits[1] != 'for': raise TemplateSyntaxError, "second argument must be 'for'"
    if bits[3] != 'with': raise TemplateSyntaxError, "fourth argument must be 'with'"
    if bits[5] != 'as': raise TemplateSyntaxError, "sixth argument must be as"
    user = parser.compile_filter(bits[2])
    settings = bits[4]
    context_var = bits[6]
    return GetSettingsNode(user,settings,context_var)

register.tag(_get_settings,'get_settings')

class GetWarningNode(Node):
    def __init__(self,user,context_var):
        self.user = user
        self.context_var = context_var

    def render(self,context):
        user = self.user.resolve(context, ignore_failures=True)
        from apps.wh.models import Warning
        from django.db.models import Q
        kw = {}
        if hasattr(user,'army'):
            if hasattr(user.army,'side'): kw.update({'type__side':user.army.side})
        warnings = Warning.objects.filter(Q(user=user,**kw))
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
def get_warning(parser,token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_warning should take 4 arguments "
    if bits[1] != 'for': raise TemplateSyntaxError, "second argument should be 'for'"
    if bits[3] != 'as': raise TemplateSyntaxError, "second argument should be 'as'"
    user = parser.compile_filter(bits[2])
    context_var = bits[4]
    return GetWarningNode(user,context_var)
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
    if len(bits) != 2 and len(bits) != 4: # get_object_meta var as varname
        raise TemplateSyntaxError("get_object_meta requires two or four arguments")
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
    if len(bits) != 2 and len(bits) != 4: # get_object_meta var as varname
        raise TemplateSyntaxError("get_content_type requires two or four arguments")
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
        instance = self.instance.resolve(context, ignore_failures=True) if self.instance else None
        app = self.init[:self.init.rindex('.')]
        _form = self.init[self.init.rindex('.')+1:]
        #module = __import__(app, 0, 0, -1)
        module = importlib.import_module(app)
        form_class = getattr(module, _form)
        context[self.varname] = form_class(request=context['request'], instance=instance) \
            if self.use_request else form_class(instance=instance)
        return ''

@register.tag
def get_form(parser, tokens):
    bits = tokens.contents.split()
    if len(bits) < 4 and len(bits) > 7 : #get_form 'apps.' for varname [use request]
        raise TemplateSyntaxError(
               "get_form  'app.model.Form' for form [use_request] instance")
    if bits[2] != 'as':
        raise TemplateSyntaxError, "the second argument must be 'as'"
    init = bits[1]
    varname = bits[3]

    use_request = bits[4] if len(bits) > 4 else ""

    if 'no_request' in use_request:
        use_request = False

    instance = bool(bits[5] if len(bits) > 5 else None)
    if instance:
        instance = parser.compile_filter(bits[5])
    return GetFormNode(init, varname, use_request, instance)
