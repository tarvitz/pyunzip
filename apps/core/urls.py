from django.conf.urls import *
from django.utils.translation import ugettext_lazy as _
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns(
    'apps.core.views',
    #url(r'^$', 'index', name='index'),
    url(r'^url/$', 'safe_url', name='safe-url'),
    # directs
    url(r'^password/restored/$', direct_to_template,
        {'template': 'static/password_restored.html'},
        name='password-restored'),
    url(r'^password/restore/initiated/$', direct_to_template,
        {'template': 'static/password_restore_initiated.html'},
        name='password-restore-initiated'),

    url('^permission/denied/$', direct_to_template,
        {'template': 'static/permission_denied.html'},
        name='permission-denied'),
    url('^currently/unavailable/$', direct_to_template,
        {'template': 'static/currently_unavailable.html'},
        name='currently-unavailable'),

    url('^mywot581220ae922fc400475a.html$', direct_to_template,
        {'template': 'static/mywot581220ae922fc400475a.html'},
        name='wot_verification'),
    url('^e1cfb81ac9ad.html$', direct_to_template,
        {'template': 'static/e1cfb81ac9ad.html'},
        name='yande-mail-verification'),
    url('^robots.txt$', 'robots',
       name='url_robots'),
    # static
    url(r'accounts/password/changed/successful/$',
        direct_to_template, {'template': 'static/password_changed.html'},
        name='password-changed'),
    url(r'gallery/image/deleted/$',
        direct_to_template,
        {'template': 'static/image_deleted.html'},
        name='image-deleted'),
    url(r'gallery/image/undeletable/$',
        direct_to_template,
        {'template': 'static/image_undeletable.html'},
        name='image-undeletable'),
    url(r'permission/denied/$',
        direct_to_template,
        {'template': 'static/permission_denied.html'},
        name='permission-denied'),
    url(r'pm/deleted/$',
        direct_to_template,
        {'template': 'static/pm_deleted.html'},
        name='pm-deleted'),
    url(r'pm/permissiondenied/$',
        direct_to_template,
        {'template': 'static/pm_denied.html'},
        name='pm-permission-denied'),
    url(r'pm/send/addresseelimiterror/$',
        direct_to_template,
        {'template': 'static/addresse_limit.html'},
        name='addressee-limit-error'),
    url(r'pm/send/senderlimiterror$',
        direct_to_template,
        {'template': 'static/sender_limit.html'},
        name='sender-limit-error'),
    url(r'pm/send/successfull/$',
        direct_to_template,
        {'template': 'static/pm_success.html'},
        name='pm-success'),
    url(r'rules/$',
        direct_to_template,
        {'template': 'static/rules.html'},
        name='rules'),
    url(r'faq/$',
        direct_to_template,
        {'template': 'static/faq.html'},
        name='faq'),
    url(r'timeout/$',
        direct_to_template,
        {'template': 'static/timeout.html'},
        name='timeout'),
    url(r'user/does/not/exist/$',
        direct_to_template,
        {'template': 'static/user_not_exists.html'},
        name='user-not-exists'),
    url(r'user/power/insufficient/$',
        direct_to_template,
        {'template': 'static/karma_power_insufficient.html'},
        name='karma-power-insufficient'),
    url(r'users/are/ident/$',
        direct_to_template,
        {'template': 'static/karma_self_alter.html'},
        name='karma-self-alter'),
    url(r'vote/invalid/object/$',
        direct_to_template,
        {'template': 'static/vote_invalid_object.html'},
        name='vote-invalid-object'),
)
