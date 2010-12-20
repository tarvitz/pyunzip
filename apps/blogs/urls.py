from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template,redirect_to
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.blogs.views',
    (r'^$','blog_index'),
    (r'^post/(?P<id>\d+)/$','show_post',{'object_model': 'blogs.post'}),
    (r'^by/tag/(?P<tag_id>\d+)/$', 'get_posts_via_tag'),
    #(r'karma/(?P<user>[\w\s]+)/$', 'show_karma'),
)


