from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.vote.views',
    url(r'vote/rate/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$',
        'vote_rate', name='rate'),
    url(r'vote/rate/(?P<app_label>[\w.]+)/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$',
        'vote_rate', name='rate'),
    url(r'vote/show/rated/(?P<id>\d+)/$','show_voted', name='view'),
    url('vote/best/(?P<app_model>[\w.]+)/$','show_best',
        name='best'),
    url('best/(?P<app_model>[\w.]+)/$','show_best',
        name='best'), #alias
    url('vote/comment/rate/(?P<id>\d+)/$','comment_rate',
        name='comment-rate'),
)


