from django.conf.urls import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.blogs.views',
    #url(r'^$','blog_index', name='index'),
    #url(r'^post/(?P<id>\d+)/$','show_post',{'object_model': 'blogs.post'}, name='post'),
    #url(r'^by/tag/(?P<tag_id>\d+)/$', 'get_posts_via_tag', name='tag'),
    #(r'karma/(?P<user>[\w\s]+)/$', 'show_karma'),
)


