from apps.wh.models import (Expression, Fraction, PM, MiniQuote, Settings)
from apps.news.models import News
from apps.files.models import Replay
from apps.core import get_skin_template
from apps.core.helpers import get_settings
from django.template.loader import get_template, TemplateDoesNotExist
from apps.helpers import get_self_ip_address

def session(request):
    return {'session': request.session}

def base_template(request):
    from django.conf import settings
    template = settings.DEFAULT_TEMPLATE
    is_auth = request.user.is_authenticated()
    skin_css_path = None
    if is_auth and request.user.skin:
        templ = "skins/%s/base.html" % (request.user.skin.name.lower())
        skin_css_path = "%(root)s/%(skin)s/main.css" % {
            'root': settings.STYLES_URL,
            'skin': request.user.skin.name.lower()
        }
        try:
            get_template(templ)
            template = templ
        except:
            pass
    return ({
        'base_template': template,
        'skin_css_path': skin_css_path
    })

def server_ip(request):
    return {'self_ipaddress':get_self_ip_address()}

# old and ugly, disabled
def expressions(request):
    #random
    try:
        miniquote = MiniQuote.objects.order_by('?')[0]
    except IndexError:
        return {} #no data in table
    if request.user.is_authenticated():
        user = request.user
        try:
            expression = Expression.objects.filter(fraction__id__exact=user.army.side.fraction.id).order_by('?')[0]
        except:
            try:
                expression = Expression.objects.order_by('?')[0]
            except Expression.DoesNotExist:
                expression = {}
    else:
        expression = Expression.objects.order_by('?')[0]
    #expression = Expression.objects.get(id__exact=1)
    return {
        'expression': expression,
        'miniquote': miniquote,
    }


def global_settings(request):
    from django.conf import settings
    return {
        'gs': settings,
        'global_settings': settings,
        'settings': {'document': settings.DOCUMENT}
    }

def global_referer(request):
    return {
        'global_referer': request.META.get('HTTP_REFERER','/'),
        'current_referer': request.META.get('PATH_INFO', '/')
    }

def briefing_news(request):
    last_news = get_settings(request.user,'last_news_amount',10)
    bn = News.objects.filter(approved=True).order_by('-date')[:last_news]
    return {
        'briefing_news': bn
    }

def last_replays(request):
    last_replays = get_settings(request.user,'last_replays_amount',10)
    reps = Replay.objects.order_by('-id')[:last_replays]
    return {
        'last_replays': reps
    }

def pm(request):
    if request.user.is_authenticated():
        user = request.user
        if user.id:
            pm_unread = PM.objects.filter(addressee=user,is_read=False,dba=False).count()
            pm_all = PM.objects.filter(addressee=user,dba=False).count()
            pm = dict()
            pm = {
                'unread':pm_unread,
                'all':pm_all
            }
            return {
                'pm':pm
            }
        else:
            return {}
    return {}

#OBSOLETE
def user_settings(request):
    """
    _settings_ = Settings()
    #settings some applies
    from apps.wh import settings as wh_settings
    user = request.user
    setattr(_settings_, 'document',dict())
    setattr(_settings_, 'gsettings',dict())
    for m in wh_settings.map:
        value = get_skin_template(user,getattr(wh_settings,m))
        key = m.replace('_TEMPLATE','').lower()
        #setattr(_settings_,'document_%s' % key,value)
        #migrating to settings.document.value with templates
        #ten minutes after: done xD
        _settings_.document[key] = value
    skin = (
        get_skin_template(request.user, "base.html")
        if user.is_authenticated() else "base.html"
    )
    """
    """
    links = get_skin_template(request.user, "links.html")
    comments = get_skin_template(request.user, "comments.html")
    comments_form = get_skin_template(request.user, "add_comments.html")
    replay_inc = get_skin_template(request.user,"replays/includes/replay.html")
    replays_inc = get_skin_template(request.user,"replays/includes/replays.html")
    """
    #usersettings = {}
    #if hasattr(request,'usersettings'): usersettings = request.usersettings
    from django.conf import settings
    #_settings_.gsettings['KARMA_COMMENTS_COUNT'] = settings.KARMA_COMMENTS_COUNT
    #settings = {
    #        'settings': settings, #_settings_,
    #}
    return settings
