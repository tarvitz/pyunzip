from django.conf.urls import *
from django.contrib.auth.decorators import login_required
from apps.tabletop import views


urlpatterns = patterns('apps.tabletop.views',
    #url('^report/add/$', 'add_battle_report',
    #    name='battle-report-add'),
    url('^report/add/$', 'report_add',
        name='report-add'),
    url('^report/(?P<pk>\d+)/edit/$', 'report_add',
        name='report-edit'),
    url('^report/(?P<pk>\d+)/approve/$',
        'report_approve',
        name='report-approve'),
    url('^report/(?P<pk>\d+)/disapprove/$',
        'report_approve',
        {'approved': False},
        name='report-disapprove'
    ),
    #url('^new/report/add/$', 'add_new_battle_report',
    #    name='url_add_new_battle_report'),
    #url('^reports/$', 'index',
    #    name='battle-reports'), #battle_report_index ? <-- stale url schema
    url('^reports/self/$', 'reports',
        name='battle-reports-self'),
    url('^reports/$', 'battle_reports',
        name='battle-reports'),
    url('^reports/(?P<pk>\d+)/$', 'report',
        name='report'),

    url('^reports/delete/(?P<id>\d+)/(?P<approve>(approve|force))/$', 'delete_battle_report',
        name='battle-report-delete'),
    url('^reports/(?P<id>\d+)/edit/$', 'add_battle_report',{'action':'edit'},
        name='battle-report-edit'),
    url('^rosters/all/$', views.RostersListView.as_view(),
        name='rosters-index'),
    url('^rosters/$', login_required(views.UserRosterListView.as_view()),
        name='rosters'),
    url('^roster/add/$', 'action_roster',
        name='roster-add'),
    url('^roster/spawn/(?P<id>\d+)/$', 'action_roster',{'action': 'spawn'},
        name='roster-spawn'),
    url('^roster/edit/(?P<id>\d+)/$', 'action_roster',{'action': 'edit'},
        name='roster-edit'),

    url('^rosters/(?P<pk>\d+)/detail/$',
        views.RosterDetailView.as_view(),
        name='roster'),
    url('^roster/unorphan/(?P<id>\d+)/$', 'unorphan',
        name='roster-unorphan'),

    url('^codex/add/$', 'action_codex',
        name='codex-add'),
    url('^codex/edit/(?P<id>\d+)/$', 'action_codex',
        {'action': 'edit'},
        name='codex-edit'),
    url('^codex/(?P<id>\d+)/$', 'show_codex',
        name='codex'),
)

