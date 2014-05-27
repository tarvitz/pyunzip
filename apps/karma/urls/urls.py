from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.karma import views

urlpatterns = patterns(
    'apps.karma.views',
    url('karma/description/(?P<codename>[\w\s-]+)/$',
        'show_karmastatus_description',
        name='status'),
    #url(r'karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s]+)/$',
    #    'alter_karma', name='alter'),
    #url(r'karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s\d]+)/$',
    #    'karma_alter', name='alter'),
    url(r'^karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s\d]+)/$',
        login_required(views.KarmaChangeView.as_view()), name='alter'),
    url(r'karma/type/(?P<type>[\w]+)/$',
        'show_karma', name='karma'),
    url(r'karma/group/$',
        'show_karma',{'group':True}, name='karma'),
    url('karma/(?P<user>[\w\s]+)/$',
        'show_karma',
        name='karma'),
    url(r'karma/(?P<user>[\w\s]+)/(?P<type>(positive|negative|zero))/$',
        'show_karma', 'karma'),
    url(r'karma/$', 'show_karma', name='self'),
)


