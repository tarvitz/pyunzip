from django.conf.urls import patterns, include, url
from apps.core.shortcuts import direct_to_template
from django.contrib.auth.decorators import login_required
from apps.accounts import views


urlpatterns = patterns(
    'apps.accounts.views',
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^profile/$',
        login_required(views.ProfileSelfView.as_view()), name='profile'),
    url(r'^profiles/(?P<pk>\d+)/$',
        login_required(views.ProfileView.as_view()),
        name='profile'),
    url(r'^profiles/(?P<slug>[\w\d\-_ ]+)/$',
        login_required(views.ProfileView.as_view()), name='profile-by-nick'),

    url(r'^account/password/(?P<sid>[\w\d]+)/restore/$',
        views.PasswordRestoreView.as_view(),
        name='password-restore'),
    url(r'^accounts/password/restore/initiate/$',
        views.PasswordRestoreInitiateView.as_view(),
        name='password-restore-initiate'),
    url(r'^accounts/password/change/$',
        login_required(views.PasswordChangeView.as_view()),
        name='password-change',
    ),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^profile/update/$', views.ProfileUpdateView.as_view(),
        name='profile-update'),
    url(r'^register/success/$', direct_to_template,
        {'template': 'accounts/register_success.html'},
        name='register-success'),
    url(r'^accounts/banned/$', direct_to_template,
        {'template': 'accounts/banned.html'}, name='banned'),
    url(r'password/changed/$', direct_to_template,
        {'template': 'accounts/password_changed.html'},
        name='password-changed'),
)
