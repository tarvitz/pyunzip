from django.conf.urls import patterns, url
from apps.core.shortcuts import direct_to_template


urlpatterns = patterns(
    'apps.wh.views.views',
    url('^sulogin/$', 'sulogin',
        name='superlogin'),

    url(r'^ranks/(?P<pk>\d+)/$', 'show_rank', name='ranks'),
    url('^ranks/(?P<codename>[\w\s]+)/$', 'show_rank',
        name='rank'),
    # static
    url(r'^registered/$', direct_to_template,
        {'template': 'accounts/registered.html'}, name='registered'),

)
