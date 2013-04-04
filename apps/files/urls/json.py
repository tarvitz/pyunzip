from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.files.views',
    url(r'^xhr/get/replay/versions/$', 'xhr_get_replay_versions',
        name='replay-get-versions'),
    url(r'^xhr/get/replay/versions/(?P<id>\d+)/$', 'xhr_get_replay_versions',
        name='replay-get-versions'),
    url('^xhr/get/img/alias/(?P<alias>[\w\d_]+)/$', 'xhr_get_img_alias',
        name='image-get-alias'),
    url('^xhr/get/img/alias/$', 'xhr_get_img_alias',
        {'alias': 0,},
        name='image-get-alias'),
)
