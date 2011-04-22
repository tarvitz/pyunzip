# Create your views here.
from apps.thirdpaty.SourceLib.SourceRcon import SourceRcon
from apps.thirdpaty.SourceLib.settings import SOURCE_SERVER as CONF
until = lambda s,e: s[:s.rindex(e)]
from apps.core.shortcuts import direct_to_template
import re

def l4d2_stat(request):
    rcon = SourceRcon(**CONF)
    reply = rcon.rcon('status')
    reply = until(reply,'# userid')
    reply = reply.strip('\n').replace('udp/ip','ip')
    reply = dict(re.findall('^(\w+).*?:\s(.*?)$',reply,re.S|re.M|re.I))
    return direct_to_template(request,'non40k/l4d2stat.html', {'l4d2':reply})
