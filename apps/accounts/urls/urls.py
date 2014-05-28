from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template
from apps.accounts import views


urlpatterns = patterns('apps.accounts.views',
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^profile/update/$', views.ProfileUpdateView.as_view(),
        name='profile-update'),
    url(r'^register/success/$', direct_to_template,
        {'template': 'accounts/register_success.html'},
        name='register-success'),
    url(r'^context/(?P<context>\d+)/set/$', 'user_set_context',
        name='context-set'),
    url(r'^context/switch/$', 'user_switch_context',
        name='context-switch'),
)
