"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from apps.thirdpaty.sleekxmpp.basexmpp import BaseXMPP
from apps.thirdpaty.sleekxmpp.clientxmpp import ClientXMPP
from apps.thirdpaty.sleekxmpp.componentxmpp import ComponentXMPP
from apps.thirdpaty.sleekxmpp.stanza import Message, Presence, Iq
from apps.thirdpaty.sleekxmpp.xmlstream.handler import *
from apps.thirdpaty.sleekxmpp.xmlstream import XMLStream, RestartStream
from apps.thirdpaty.sleekxmpp.xmlstream.matcher import *
from apps.thirdpaty.sleekxmpp.xmlstream.stanzabase import StanzaBase, ET
