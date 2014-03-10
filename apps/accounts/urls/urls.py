from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template
from apps.accounts.views import (
    UpdateRequestView, RequestListView, CreateAccountView, CreateRoleView,
    RoleListView, UpdateRoleView, ProfileView, ProfileUpdateView
)


urlpatterns = patterns('apps.accounts.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^profile/update/$', ProfileUpdateView.as_view(),
        name='profile-update'),
    url(r'^register/$', 'register', name='register'),
    url(r'^register/success/$', direct_to_template,
        {'template': 'accounts/register_success.html'},
        name='register-success'),
    url(r'requests/$', RequestListView.as_view(),
        name='requests'),
    url(r'requests/(?P<pk>\d+)/update/$',
        UpdateRequestView.as_view(), name='request-update'),
    url(r'requests/(?P<pk>\d+)/create/account/$', CreateAccountView.as_view(),
        name='request-create-account'),
    url(r'^context/(?P<context>\d+)/set/$', 'user_set_context',
        name='context-set'),
    url(r'^context/switch/$', 'user_switch_context',
        name='context-switch'),
    url(r'^roles/$', RoleListView.as_view(),
        name='roles'),
    url(r'^roles/create/$', CreateRoleView.as_view(),
        name='role-create'),
    url(r'^roles/(?P<pk>\d+)/update/$', UpdateRoleView.as_view(),
        name='role-update')
)
