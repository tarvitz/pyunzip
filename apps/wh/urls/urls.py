from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
#from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns(
    'apps.wh.views.views',
    url('^sulogin/$', 'sulogin',
        name='superlogin'),
    url(r'^accounts/$', 'users', name='users'),
    #todo: move to json
    url('^accounts/get/users/$','x_get_users_list',
        name='url_x_get_users_list_null'),
    url('^accounts/get/users/(?P<nick_part>[\w\s-]+)/$','x_get_users_list',
        name='url_x_get_users_list'),
    #endtodo
    url(r'^accounts/update/profile/successfull/$', direct_to_template,
        {'template': 'accounts/updated.html'}),
    url('^accounts/get/avatar/(?P<nickname>[\w\s-]+)/$', 'get_user_avatar',
        name='avatar'),

    url(r'^pm/$','pm', name='pm'),
    url(r'^pm/send/$', 'pm_send', name='pm-send'),
    url(r'^pm/(?P<pk>\d+)/delete/$', 'pm_delete', name='pm-delete'),
    url(r'^pm/(?P<pm_id>\d+)/$', 'view_pm', name='pm-view'),
    url(r'^pm/(?P<pm_id>\d+)/delete/(?P<approve>(approve|force))/$', 'delete_pm', name='pm-delete'),
    url(r'^pm/(?P<pm_id>\d+)/delete/$', 'delete_pm', name='pm-delete'),

    url(r'^ranks/(?P<pk>\d+)/$', 'show_rank', name='ranks'),
    url('^ranks/(?P<codename>[\w\s]+)/$', 'show_rank',
        name='rank'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/$', 'get_rank', name='rank-get'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/formatted/$', 'get_rank', {'raw':False}, name='rank-get-raw'), #todo: move to json
    url('^warnings/(?P<nickname>[\w\s]+)/(?P<typ>(increase|decrease))/$', 'alter_warning',
        name='warning-alter'),
    url('^warnings/alter/(?P<nickname>[\w\s]+)/$', 'alter_warning_form',
        name='warning-alter-form'),
    #url(r'^miniquote/get/raw', 'get_miniquote_raw', name='miniquote-get-raw'), # todo: move to json
    #url(r'^favicon.ico$', 'favicon', name='favicon'),
    # static
    url(r'^registered/$', direct_to_template,
        {'template': 'accounts/registered.html'}, name='registered'
    ),
    #url(r'password/recovered/$', direct_to_template,
    #    {'template': 'accounts/password_changed.html'},
    #    name='password-changed'
    #)
)
