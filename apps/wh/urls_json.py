from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.wh.views',
    url('^get/miniquote/$', 'get_miniquote_raw',
        name='miniquote'),
    url(r'^get/armies/$', 'xhr_get_armies',
        name='armies'),
    url(r'^get/armies/(?P<id>\d+)/$', 'xhr_get_armies',
        name='armies'),
)
