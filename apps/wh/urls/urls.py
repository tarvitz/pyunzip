from django.conf.urls import url
from apps.core.shortcuts import direct_to_template

from ..views import views


urlpatterns = [
    url('^sulogin/$', views.sulogin,
        name='superlogin'),

    url(r'^ranks/(?P<pk>\d+)/$', views.show_rank, name='ranks'),
    url('^ranks/(?P<codename>[\w\s]+)/$', views.show_rank,
        name='rank'),
    # static
    url(r'^registered/$', direct_to_template,
        {'template': 'accounts/registered.html'}, name='registered'),
]
