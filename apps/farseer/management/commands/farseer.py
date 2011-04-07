# coding: utf-8
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from apps.farseer.seer import SeerBot
import logging
logger = logging.getLogger(__name__)
from apps.farseer.settings import *

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--user', '-u', dest='jid',
            help='changes jabber user account'),
        make_option('--password', '-P', dest='password',
            help='changes jabber password for account'),
        make_option('--server', '-s', dest='server',
            help='jabber server'),
        make_option('--port', '-p', dest='port',
            help='jabber server port'),
    )
    help = """farseer jabber bot"""

    def handle(self, **options):
        jid = options.get('jid',None) or BOT_JID
        password = options.get('password',None) or BOT_PASSWORD
        if not jid or not password:
            print "please pass valid options for jabberbot connection"
            from sys import exit
            exit(-1)
        server = options.get('server','localhost')
        port = options.get('port',5222)
        xmpp = SeerBot(jid,password)
        xmpp.registerPlugin('xep_0030') # Service Discovery
        xmpp.registerPlugin('xep_0004') # Data Forms
        xmpp.registerPlugin('xep_0060') # PubSub
        xmpp.registerPlugin('xep_0199') # XMPP Ping
        if xmpp.connect((BOT_SERVER,BOT_PORT)):
            xmpp.process(threaded=True)
            logger.info("connection complete")
        else:
            logger.error("unable to connect.")


