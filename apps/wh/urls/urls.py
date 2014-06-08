from django.conf.urls import patterns, url
from apps.core.shortcuts import direct_to_template


urlpatterns = patterns(
    'apps.wh.views.views',
    url('^sulogin/$', 'sulogin',
        name='superlogin'),
    url(r'^accounts/$', 'users', name='users'),

    url(r'^accounts/update/profile/successfull/$', direct_to_template,
        {'template': 'accounts/updated.html'}),
    url(r'^ranks/(?P<pk>\d+)/$', 'show_rank', name='ranks'),
    url('^ranks/(?P<codename>[\w\s]+)/$', 'show_rank',
        name='rank'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/$', 'get_rank', name='rank-get'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/formatted/$', 'get_rank', {'raw':False}, name='rank-get-raw'), #todo: move to json
    url('^warnings/(?P<nickname>[\w\s]+)/(?P<typ>(increase|decrease))/$', 'alter_warning',
        name='warning-alter'),
    url('^warnings/alter/(?P<nickname>[\w\s]+)/$', 'alter_warning_form',
        name='warning-alter-form'),

    # static
    url(r'^registered/$', direct_to_template,
        {'template': 'accounts/registered.html'}, name='registered'),

)
