"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

from apps.thirdpaty.sleekxmpp.xmlstream.handler.callback import Callback
from apps.thirdpaty.sleekxmpp.xmlstream.handler.waiter import Waiter
from apps.thirdpaty.sleekxmpp.xmlstream.handler.xmlcallback import XMLCallback
from apps.thirdpaty.sleekxmpp.xmlstream.handler.xmlwaiter import XMLWaiter

__all__ = ['Callback', 'Waiter', 'XMLCallback', 'XMLWaiter']
