# coding: utf-8
from django.utils.translation import ugettext_lazy as _

#syntaxes enabled on site
#SYNTAX=(('markdown','markdown'),('bb-code','bb-code'),('textile','textile'),('creole', 'wiki'),)
SYNTAX = (('textile', 'textile'), ('bb-code', 'bb-code'),)

SIGN_CHOICES = (
        (1, '[*]'),
        (2, '[*][*]'),
        (3, '[+]'),
        (4, '[+][+]'),
        (5, '[x]'),
        (6, '[x][x]'),
        (7, _('[ban]')),
        (8, _('[everban]')),
)

#OTHER SETTINGS
READONLY_LEVEL = 5
GLOBAL_SITE_NAME = 'http://w40k.net'
