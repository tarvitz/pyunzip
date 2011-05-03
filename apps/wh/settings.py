# coding: utf-8
# SOME SKIN SETTINGS ARE HERE
from django.utils.translation import ugettext_lazy as _

map = ['LINKS_TEMPLATE','COMMENTS_TEMPLATE','REPLAY_INC_TEMPLATE','COMMENTS_FORM_TEMPLATE',
    'REPLAYS_INC_TEMPLATE','SEARCH_INC_TEMPLATE','NEWS_INC_TEMPLATE','ARTICLE_INC',
    'ROSTERS_INC_TEMPLATE','ROSTER_INC_TEMPLATE','BATTLE_REPORT_INC',
    'NOTHING_INC','IMAGE_INC_TEMPLATE']

LINKS_TEMPLATE = 'links.html'
COMMENTS_TEMPLATE = 'comments.html'
REPLAY_INC_TEMPLATE = 'replays/includes/replay.html'
REPLAYS_INC_TEMPLATE = 'replays/includes/replays.html'
COMMENTS_FORM_TEMPLATE = 'add_comments_ng.html'
SEARCH_INC_TEMPLATE = 'includes/search.html'
NEWS_INC_TEMPLATE = 'includes/news.html'
ROSTERS_INC_TEMPLATE = 'includes/rosters.html'
ROSTER_INC_TEMPLATE = 'includes/roster.html'
BATTLE_REPORT_INC = 'includes/battle_report.html'
NOTHING_INC = 'nothing.html'
ARTICLE_INC = "includes/article.html"
IMAGE_INC_TEMPLATE = 'gallery/includes/image.html'

#syntaxes enabled on site
SYNTAX=(('markdown','markdown'),('bb-code','bb-code'),('creole', 'wiki'),)
SIGN_CHOICES = (
        (1,'[*]'),
        (2,'[*][*]'),
        (3,'[+]'),
        (4,'[+][+]'),
        (5,'[x]'),
        (6,'[x][x]'),
        (7,_('[ban]')),
        (8,_('[everban]')),
)

#OTHER SETTINGS
READONLY_LEVEL=5
GLOBAL_SITE_NAME='http://tarvitz.no-ip.org'
