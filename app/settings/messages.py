# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
INVITE_MESSAGE = _("""
    
    %(user)s Greatings you and whole blacklibrary administration.
    You have been invited to b3ban.blacklibrary.ru.
    If you don't know whats this site/service does please ignore it or wait
    for explanation from your friends playing in battlefield 3.
    Please click follow the %(link)s and follow given instructions
    to proceed the registration.

    If you got this letter accidently, please ignore it, nothing bad would happen :)

    Sincerely your b3ban.blacklibrary.ru administration
""")
PASSWORD_RESTORE_REQUEST_MESSAGE = _("""
    Your or somebody else requested password change for this email account.
    If you're not the person who initiated password request procedure, please ignore
    this letter or give a notice for service administration:
    http://b3ban.blacklibrary.ru/contacts/

    Your password restore link: %(link)s
""")
ARICLE_REJECTED_NOTIFICATION = _("""
    Article you wrote had been rejected with reason: %(reason)s
    Please fix the errors, mistakes and anything that reason says to
    get the article posted on title page.

    Thank you :)
""")
