from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.tracker.views',
    url('^xhr/mark/read/$',
        'xhr_mark_read', { 'app_n_model': 'None.None', 'id': 0 },
        name='mark-read'),
    url('^xhr/mark/read/(?P<app_n_model>[\w.]+)/(?P<id>\d+)/$',
        'xhr_mark_read',
        name='mark-read'),
)
