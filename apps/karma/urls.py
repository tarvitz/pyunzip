from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.karma.views',
    #(r'vote/rate/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$', 'vote_rate'),
    #(r'vote/rate/(?P<app_label>[\w.]+)/(?P<model_name>[\w.]+)/(?P<obj_id>\d+)/(?P<rate>\d+)/$', 'vote_rate'),
    #(r'vote/show/rated/(?P<id>\d+)/$','show_voted'),
    (r'karma/up/$','up'),
    (r'karma/down/$','down'),
    #;) let it be the secret for all
    #(r'karma/description/(?P<id>\d+)/$','show_karmastatus_description'),
    url('karma/description/(?P<codename>[\w\s-]+)/$','show_karmastatus_description',
        name='url_karma_status'),
    (r'karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s]+)/$', 'alter_karma'),
    (r'karma/type/(?P<type>[\w]+)/$','show_karma'),
    (r'karma/group/$', 'show_karma',{'group':True}),
    url('karma/(?P<user>[\w\s]+)/$', 'show_karma',
        name='url_karma_user'),
    (r'karma/(?P<user>[\w\s]+)/(?P<type>(positive|negative|zero))/$', 'show_karma'),
    (r'karma/$','show_karma'),
)


