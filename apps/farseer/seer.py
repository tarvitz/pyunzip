#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
#sys.path.insert(0,'/home/www/warmist')
import logging
import time
import socket
import thread
import re
from optparse import OptionParser

from apps.thirdpaty import sleekxmpp
import logging
logger = logging.getLogger(__name__)

HELP_TEXT = """
'help' - show current list of commands
'send_test_message' - sends for all subscribed users test message
'terminate_bot' or 'terminate - close session and quit
'send_notification' <jid:<USERJID> message:<MESSAGE>>
's_notify' is alias to 'send_notification'
"""
HELP_JABBER = """
!help - shows this message
!test - tests authorized message send
!get_roster - shows bot's roster
!get_subscribed - shows bot's rosters filters everyone who has subscription both or to
!get_last_news - shows last news
!whoami - shows who are you :D
"""
# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
until = lambda s,e: s[:s.rindex(e)] 
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

RESOURCE = 'AstroPath'

class SeerBot(sleekxmpp.ClientXMPP):

    """
    A simple SeerBot bot that will act withing network interface
    which is runned on 40001 and accepts commands from local connections only
    """

    def __init__(self, jid, password):
        #altering resource
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.boundjid.resource = RESOURCE
        #may cause disconnects
        #self.set_jid("%s/%s" % (JID,RESOURCE))
        
        #thread.start_new_thread(self.net_listen,())
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can intialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)
        self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def msg_url_preprocess(self,scheme):
        pass
        
    #============ Network ================ 
    #
    #=====================================
    
    def net_listen(self):
        self.ip = 'localhost'
        self.port = 40001
        #sockobj = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.sockobj.bind((self.ip,self.port))
            self.sockobj.listen(5) #5 requests
        except socket.error as (errno,errmsg):
            logger.error("port is already opened")
            self.sockobj.close()
            self.disconnect()
            sys.exit(-1)
            return
        
        while True:
            connection, address = self.sockobj.accept()
            logger.info("(%s:%s) connected" % address)
            if address[0] != '127.0.0.1':
                connection.send('only local connection permitted')
                connection.close()
            else:
                while True:
                    data = connection.recv(1024) #ugly?
                    if not data: break
                    #connection.send("Echo=>"+data)
                    connection.send('recieved: '+data)
                    self.process_net_msg(connection,data)
                connection.close()
    
    def process_net_msg(self,connection,data):
        if ' ' in data:
            command = data[:data.index(' ')]
        else:
            command = data
        
        data = str(data).strip('\r').strip('\n')
        logger.info('data: %r',data)
        if 'help' in command:
            connection.send(HELP_TEXT)
        elif 'send_test_message' in command:
            self.send_authorized_message('chat', 'test message via socket force ;)')
        elif 'terminate_bot' in command:
            logger.info('FarSeer bot termination command catch\nexiting..')
            self.sockobj.close()
            self.disconnect()
            from sys import exit
            exit(0)
        elif 'send_notification' or 's_notify' in command:
            jid,message = None,None
            try:
                jid = re.findall(re.compile(r'jid:([\w\._]+@[\w\._]+)',re.U|re.S),data)[0]
                message = re.findall(re.compile(r'message:(.*)',re.U|re.S|re.I),data)[0]
            except IndexError as (errmsg):
                logger.info(errmsg)
            if jid is None and message is None: return
            m = {'mto':jid,'mfrom':self.boundjid._full,'mtype':'chat','mbody':unicode(message)}
            self.send_message(**m)
            logger.info("sending notification to '%s'", m['mto'])
        else:
            pass
        return
    
    def process(self,threaded=False):
        #fork process with reading data
        #self.net_listen()
        thread.start_new_thread(self.net_listen,()) #socket network command interface
        super(sleekxmpp.ClientXMPP,self).process(threaded) #bot thread
        
    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an intial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.getRoster()
        self.sendPresence()
        
    #================== Messages block ===================
    #
    #=====================================================
    
    def send_authorized_message(self,mtype,mbody):
        """ Sends Authorized users message """
        m = {'mfrom':self.boundjid._full,'mtype':mtype,'mbody':mbody}
        auth_list = [r for r in self.roster.keys() if self.roster[r]['subscription'] in ('to','both')]
        for user in auth_list:
            m.update({'mto':user})
            self.send_message(**m)  
    
    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if '!help' in msg['body']:
            m = {'mtype':'chat', 'mto': msg['from'],'mfrom':msg['to'],'mbody':HELP_JABBER}
            self.send_message(**m)
            
        elif '!get_roster' in msg['body']:
            #msg.reply("Get Roster initiated").send()
            #roster = msg.stream.roster
            message = ''
            for r in self.roster.keys():
                message += r+'\n'
                #    def send_message(self, mto, mbody, msubject=None, mtype=None,
                #     mhtml=None, mfrom=None, mnick=None):
                #m = dict() # it appears to be Message object. but ну его нахуй
                #m['mtype'] = 'chat'
                #m['mto'] = msg['from'] #ehm?
                #m['mfrom'] = msg['to'] #construct from reply
                ##m['id'] = '0xdead'
                #m['mbody'] = r
                #if r == 'lilfox@krctc':
            m = {'mto':msg['from'],'mfrom':msg['to'],'mtype':'chat','mbody':message}
            self.send_message(**m)
                
        elif '!get_subscribed' in msg['body']:
            #roster = msg.stream.roster
            roster_list = ''
            for r in self.roster.keys():
                if self.roster[r]['subscription'] in ('to','both'):
                    #single message
                    #m = {'mtype':'chat', 'mto': msg['from'],'mfrom':msg['to'],'mbody':r}
                    #self.send_message(**m)
                    #reply (works once!)
                    roster_list+="%s\n" % r
            msg.reply(roster_list).send()
        elif "!get_last_news" in msg['body']:
            from apps.news.models import News
            n = News.objects.all()
            if n: n=n[0]
            m = {'mto':msg['from'],'mfrom':msg['to'],'mtype':'chat','mbody':"%s\n%s" % (n.title,n.get_content_plain())}
            self.send_message(**m)
        elif "!test" in msg['body']:
            self.send_authorized_message('chat', 'test message')
        elif '!whoami' in msg['body']:
            from django.contrib.auth.models import User
            m = {'mto':msg['from'],'mfrom':self.boundjid.full,'mtype':'chat'}
            jid = msg['from']._jid #<-- nya?
            if '/' in jid: jid = until(jid,'/')
            u = User.objects.filter(jid=jid)
            if u:
                m.update({'mbody':'Registered user'})
            else:
                m.update({'mbody':'Unregistered user'})
            self.send_message(**m)
        else:
            msg.reply("please enter !help to get whole list of the commands" % msg).send()



#Debug
if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    jid,password = "farseer@inferno:farseer".split(':')
    xmpp = SeerBot(jid,password)
    xmpp.registerPlugin('xep_0030') # Service Discovery
    xmpp.registerPlugin('xep_0004') # Data Forms
    xmpp.registerPlugin('xep_0060') # PubSub
    xmpp.registerPlugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the pydns library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(threaded=False)
        logger.info('Seer: connection complete')
    else:
        logger.error("Seer: Unable to connect.")
