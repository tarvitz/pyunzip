from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.karma.views import views

urlpatterns = [
    url(r'^karma/$', login_required(views.KarmaListView.as_view()),
        name='karma-list'),
    url(r'^karma/(?P<pk>\d+)/$',
        login_required(views.KarmaListView.as_view()),
        name='karma-list'),

    url(r'^karma/alter/(?P<choice>(up|down))/(?P<nickname>[\w\s\d\.]+)/$',
        login_required(views.KarmaChangeView.as_view()), name='karma-alter'),
]
