from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from apps.tabletop import views


urlpatterns = patterns(
    'apps.tabletop.views',

    url('^rosters/all/$', views.RostersListView.as_view(),
        name='rosters-index'),
    url('^rosters/$', login_required(views.UserRosterListView.as_view()),
        name='rosters'),
    url('^roster/add/$', login_required(views.RosterCreateView.as_view()),
        name='roster-add'),
    url('^roster/edit/(?P<pk>\d+)/$',
        login_required(views.RosterUpdateView.as_view()),
        name='roster-edit'),
    url('^roster/(?P<pk>\d+)/delete/$',
        login_required(views.RosterDeleteView.as_view()), name='roster-delete'),
    url('^rosters/(?P<pk>\d+)/detail/$',
        views.RosterDetailView.as_view(),
        name='roster'),

    url('^codexes/add/$',
        login_required(views.CodexCreateView.as_view()),
        name='codex-add'),
    url('^codexes/(?P<pk>\d+)/edit/$',
        login_required(views.CodexUpdateView.as_view()),
        name='codex-edit'),
    url('^codexes/(?P<pk>\d+)/delete/$',
        login_required(views.CodexDeleteView.as_view()),
        name='codex-delete'),
    url('^codexes/(?P<pk>\d+)/$',
        login_required(views.CodexDetailView.as_view()),
        name='codex-detail'),
    url('^codexes/$', login_required(views.CodexListView.as_view()),
        name='codex-list'),

    url('^reports/add/$',
        login_required(views.ReportCreateView.as_view()),
        name='report-create'),
    url('^reports/(?P<pk>\d+)/edit/$',
        login_required(views.ReportUpdateView.as_view()),
        name='report-update'),
    url('^reports/(?P<pk>\d+)/delete/$',
        login_required(views.ReportDeleteView.as_view()),
        name='report-delete'),
    url('^reports/(?P<pk>\d+)/$',
        views.ReportDetailView.as_view(),
        name='report-detail'),
    url('^reports/$',
        views.ReportListView.as_view(),
        name='report-list'),
)
