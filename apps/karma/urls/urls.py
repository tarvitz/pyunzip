from django.conf.urls import *
from django.contrib.auth.decorators import login_required

from apps.karma import views

urlpatterns = patterns(
    'apps.karma.views',
    url(r'^karma/$', login_required(views.KarmaListView.as_view()),
        name='karma-list'),
    url(r'^karma/(?P<pk>\d+)/$',
        login_required(views.KarmaListView.as_view()),
        name='karma-list'),

    url(r'^karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s\d]+)/$',
        login_required(views.KarmaChangeView.as_view()), name='karma-alter'),
)
