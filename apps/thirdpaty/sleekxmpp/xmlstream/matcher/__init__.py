"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from apps.thirdpaty.sleekxmpp.xmlstream.matcher.id import MatcherId
from apps.thirdpaty.sleekxmpp.xmlstream.matcher.many import MatchMany
from apps.thirdpaty.sleekxmpp.xmlstream.matcher.stanzapath import StanzaPath
from apps.thirdpaty.sleekxmpp.xmlstream.matcher.xmlmask import MatchXMLMask
from apps.thirdpaty.sleekxmpp.xmlstream.matcher.xpath import MatchXPath

__all__ = ['MatcherId', 'MatchMany', 'StanzaPath',
           'MatchXMLMask', 'MatchXPath']
