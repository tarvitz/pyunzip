# coding : utf-8
# Jabber Bot Decorators
from django.contrib.auth.models import User
from apps.core.helpers import get_object_or_none
until = lambda s,e: s[:s.index(e)]
import logging
logger = logging.getLogger(__name__)

def su_required(func):
    def wrapper(*args,**kwargs):
        self = args[0]
        msg = args[1]
        jid = msg['from']._jid
        if '/' in jid: jid = until(jid,'/')
        logger.info('jid: %s\nself.jid: %s' % (jid,self.JID))
        u = get_object_or_none(User,jid=jid)
        logger.info('user: %r' % u)
        if u:
            return func(*args,**kwargs)
        else: 
            m = {'mto':msg['from'],'mfrom':msg['to'],'mtype':'chat','mbody':'You have not enough permissions to do this ;)'}
            self.send_message(**m)
    return wrapper
