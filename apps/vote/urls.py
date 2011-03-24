from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.vote.views',
    (r'vote/rate/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$', 'vote_rate'),
    (r'vote/rate/(?P<app_label>[\w.]+)/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$', 'vote_rate'),
    (r'vote/show/rated/(?P<id>\d+)/$','show_voted'),
    url('vote/best/(?P<app_model>[\w.]+)/$','show_best',
        name='url_show_best'),
    url('best/(?P<app_model>[\w.]+)/$','show_best',
        name='url_show_best'), #alias
    url('vote/comment/rate/(?P<id>\d+)/$','comment_rate',
        name='url_comment_rate'),
)


