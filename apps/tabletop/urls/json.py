from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.tabletop.views',
    #xhr
    url('^rosters/$','xhr_rosters', {'search': 'test'},
        name='rosters-search'),
    url('^rosters/(?P<search>[\w\s_]+)/$','xhr_rosters', name='rosters-search'),
    url('^get/roster/(?P<id>\d+)/$', 'xhr_get_roster', name='roster'),
    url('^get/codex/revisions/$', 'xhr_get_codex_revisions',
        name='codex-revisions'),
    url('^get/codex/revisions/(?P<id>\d+)/$', 'xhr_get_codex_revisions',
        name='codex-revisions'),
)
