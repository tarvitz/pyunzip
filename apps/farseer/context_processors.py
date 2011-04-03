import re
from apps.core import get_skin_template
from apps.core.helpers import get_settings
from apps.farseer.models import Discount
from django.template.loader import get_template, TemplateDoesNotExist
from apps.thirdpaty.SourceLib.SourceRcon import SourceRcon
from apps.thirdpaty.SourceLib.settings import SOURCE_SERVER as CONF
until = lambda s,e: s[:s.rindex(e)]
import logging
logger = logging.getLogger(__name__)

def steam_discounts(request):
    return {'steam_discounts':Discount.objects.all()}

def l4d2_stats(request):
    reply = {}
    if request.user.is_authenticated():
        if request.user.settings.get('show_l4d2_stats',False):
            rcon = SourceRcon(**CONF)
            reply = rcon.rcon('status')
            reply = until(reply,'# userid')
            logger.info(reply)
            reply = reply.strip('\n').replace('udp/ip','ip')
            reply = dict(re.findall('^(\w+).*?:\s(.*?)$',reply,re.S|re.M|re.I))
            logger.info(reply)
    return {'l4d2':reply}
