from django.conf.urls import patterns, url


urlpatterns = patterns(
    'apps.tabletop.views',
    url('^rosters/$','xhr_rosters', {'search': 'test'},
        name='rosters-search'),
    url('^rosters/(?P<search>[\w\s_]+)/$', 'xhr_rosters',
        name='rosters-search'),
)

urlpatterns += patterns(
    'apps.tabletop.views.json',
)
