from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template
from django.contrib.auth.decorators import login_required
from apps.accounts import views


urlpatterns = patterns('apps.accounts.views',
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^profile/$',
        login_required(views.ProfileSelfView.as_view()), name='profile'),
    url(r'^profiles/(?P<pk>\d+)/$',
        login_required(views.ProfileView.as_view()),
        name='profile'),
    url(r'^profiles/(?P<slug>[\w\d\-\_\ ]+)/$',
        login_required(views.ProfileView.as_view()), name='profile-by-nick'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^profile/update/$', views.ProfileUpdateView.as_view(),
        name='profile-update'),
    url(r'^register/success/$', direct_to_template,
        {'template': 'accounts/register_success.html'},
        name='register-success'),
    url(r'^context/(?P<context>\d+)/set/$', 'user_set_context',
        name='context-set'),
    url(r'^context/switch/$', 'user_switch_context',
        name='context-switch'),

    url(r'^accounts/banned/$', direct_to_template,
        {'template': 'accounts/banned.html'}, name='banned')
)
