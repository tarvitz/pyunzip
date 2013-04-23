from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.wh.views',
    url('^login/$', 'login', name='login'),
    url('^sulogin/$', 'sulogin',
        name='superlogin'),
    url('^accounts/login/$', 'login', name='login'),
    url('^logout/$', 'logout', name='logout'),
    url('^accounts/password/change/$', 'change_password', name='password-change'),
    #url(r'^password/recover/$', 'password_recover', name='password-recover'),
    # new password restore
    url(r'password/(?P<sid>[\w\d]+)/restore/$', 'password_restore',
        name='password-restore'),
    url(r'password/restore/initiate/$', 'password_restore_initiate',
        name='password-restore-initiate'),
    # new password change
    #url(r'profile/password/change/$', 'password_change',
    #    name='password-change'),
    url(r'password/changed/$', direct_to_template,
        {'template': 'accounts/password_changed.html'},
        name='password-changed'),
    # end of new password restore
    url(r'^accounts/profile/$', 'profile', name='profile'),
    url('^accounts/profile/real/(?P<account_name>[\w\s-]+)/$', 'profile',
        name='profile-real'),
    url('^accounts/profile/(?P<nickname>[\w\s-]+)/$', 'profile_by_nick',
        name='profile-by-nick'),
    url(r'^accounts/$', 'users', name='users'),
    #todo: move to json
    url('^accounts/get/users/$','x_get_users_list',
        name='url_x_get_users_list_null'),
    url('^accounts/get/users/(?P<nick_part>[\w\s-]+)/$','x_get_users_list',
        name='url_x_get_users_list'),
    #endtodo
    url(r'^accounts/old_update/profile/$', 'update_profile_old'),
    url(r'^accounts/update/profile/successfull/$', direct_to_template,
        {'template': 'accounts/updated.html'}),
    url(r'^accounts/update/profile/$', 'update_profile',
        name='profile-update'),
    url('^accounts/get/avatar/(?P<nickname>[\w\s-]+)/$', 'get_user_avatar',
        name='avatar'),
    url('^accounts/get/photo/(?P<nickname>[\w\s-]+)/$', 'get_user_photo',
        name='photo'),
    url('^get/race/icon/(?P<race>[\w\s-]+)/$','get_race_icon',
        name='race-icon'),
    url(r'^accounts/get/side/icon/(?P<nickname>[\w\s-]+)/$','get_user_side_icon',
        name='user-side-icon'),
    #deprecated use xhr instead of this, todo: cleanse
    url(r'^accounts/get/armies/(?P<id>\d+)/$', 'get_armies_raw',
        name='armies-raw'),
    url(r'^accounts/get/skins/(?P<id>\d+)/$', 'get_skins_raw',
        name='skins-raw'),
    #url(r'^test/upload_avatar/$', 'upload_avatar'),
    #url(r'^test/armies_list/$', 'armies_list'),
    #url(r'^test/profile/$', direct_to_template,
    #    {'template':'accounts/test.html'}),
    #end of deprecated and test, need to be cleansed
    url(r'^pm/$','pm_view', name='pm-view'),
    url('^pm/send/user/(?P<nickname>[\w\s-]+)/$', 'send_pm',
        name='pm-send-nick'),
    url('^pm/send/$', 'send_pm',
        name='pm-send'),
    url(r'^pm/sent/$', 'view_pms', {'outcome': True}, 'pm-sent'),
    url(r'^pm/income/$','view_pms', name='pm-income'),
    url(r'^pm/(?P<pm_id>\d+)/$', 'view_pm', name='pm-view'),
    url(r'^pm/(?P<pm_id>\d+)/delete/(?P<approve>(approve|force))/$', 'delete_pm', name='pm-delete'),
    url(r'^pm/(?P<pm_id>\d+)/delete/$', 'delete_pm', name='pm-delete'),
    url(r'^register/$', 'onsite_register', name='register'),
    url(r'^register/get_math_image/$', 'get_math_image', name='math-image'), #for joke sake
    url(r'^register/get_math_image/(?P<sid>\w+)/$','get_math_image', name='math-image'),
    url(r'^ranks/(?P<id>\d+)/$', 'show_rank', name='ranks'),
    url('^ranks/(?P<codename>[\w\s]+)/$', 'show_rank',
        name='rank'),
    #url(r'^ranks/(?P<codename>[\w\s]+)/update/$', 'edit_rank', name='rank-edit'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/$', 'get_rank', name='rank-get'),
    url(r'^ranks/(?P<codename>[\w\s]+)/get/formatted/$', 'get_rank', {'raw':False}, name='rank-get-raw'), #todo: move to json
    url('^warnings/(?P<nickname>[\w\s]+)/(?P<type>(increase|decrease))/$', 'alter_warning',
        name='warning-alter'),
    url('^warnings/alter/(?P<nickname>[\w\s]+)/$', 'alter_warning_form',
        name='warning-alter-form'),
    #url(r'^miniquote/get/raw', 'get_miniquote_raw', name='miniquote-get-raw'), # todo: move to json
    url(r'^favicon.ico$', 'favicon', name='favicon'),
    # static
    url(r'^registered/$', direct_to_template,
        {'template': 'accounts/registered.html'}, name='registered'
    ),
    url(r'password/recovered/$', direct_to_template,
        {'template': 'accounts/password_changed.html'},
        name='password-changed'
    )
)