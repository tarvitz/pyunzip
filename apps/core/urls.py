from django.conf.urls import *
from django.utils.translation import ugettext_lazy as _
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns('apps.core.views',
    #(r'^search/$', 'search', name='search'),
    #(r'^search/(?P<model>\w+)/$', 'search_model'),
    url(r'^search/(?P<model>\w+)/$', 'sphinx_search_model',
        name='search-sph-model'),
    url(r'^search/$', 'sphinx_search',
        name='search-sph'),
    url(r'^settings/$','user_settings', name='settings'),
    url(r'^settings/store/(?P<key>[\w_]+)/(?P<value>\w+)/$','set_settings'),
    url(r'^subscription/$','view_subscription',
        name='subscription'),
    url(r'^unsubscribe/(?P<id>\d+)/$','delete_subscription', name='unsubscribe'),
    url('^add/comment/$', 'save_comment', name='comment-add'),
    url('^edit/comment/(?P<id>\d+)/', 'edit_comment', name='comment-edit'),
    url('^show/comments/(?P<model>[\w\s]+)/(?P<object_pk>[\w\s]+)/$','show_comments',
        name='comments'),
    url('^upload/get/progress/$','uploader_progress',name='url_upload_progress'),
    url('^xhr/upload/(?P<app_n_model>[\w\.]+)/$', 'upload_file',name='url_progress_uploader'),
    #deprecated, cleanse
    url('^upload/(?P<app_n_model>[\w\.]+)/(?P<filefield>\w+)/$', 'upload_file',name='url_progress_uploader'),
    #comments
    url('^comment/(?P<id>\d+)/(?P<flag>(delete|restore))/$', 'del_restore_comment',
        name='comment-del-restore'), #do delete,restore
    #here is a half-a-fake function, that will be completed via core.views.approve_action, see core.urls :)
    url('^comment/(?P<id>\d+)/purge/(?P<approve>(approve|force))/$','purge_comment',
        name='comment-purge'),
    #ajax integration
    url(r'^comment/(?P<id>\d+)/update/$', 'edit_comment_ajax', name='comment-edit-ajax'),
    url(r'^comment/(?P<id>\d+)/get/$', 'get_comment', name='comment-get'), #json format reply
    url(r'^comment/(?P<id>\d+)/get/raw/$', 'get_comment', {'raw':True}, name='comment-get'), #json format reply

    url(r'^gallery/image/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
        'message': _('Do you realy want to delete this image?'),
        #'url': '/gallery/image/\%s/delete/',
        'action_function': 'apps.files.views.action_image',
        'action_type': 'delete',
        }, name='approve-action'
    ),
    url(r'article/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
        'action_type': 'delete',
        'message': _('Do you realy want to delete this article?'),
        'action_function': 'apps.news.views.article_action',
        }, name='url_article_delete_approve',
    ),
    url(r'^comment/(?P<obj_id>\d+)/purge/approve/$', 'approve_action',
        {
          #'url': '/comment/\%s/purge/',
          'message': _('Do you realy want to purge this comment? O_O.. realy?'),
          'action_function': 'apps.news.views.purge_comment',
        }, name='comment-approve'
    ), #ask to purge
    url(r'^replays/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to purge this replay?'),
            'action_function': 'apps.files.views.do_purge_replay',
        }
    ),
    url(r'^pm/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to delete this comment?'),
            'action_function': 'apps.wh.views.delete_pm',
            'pk': 'pm_id',
        },
    ),
    url(r'^roster/delete/(?P<obj_id>\d+)/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to delete this roster?'),
            'action_function': 'apps.tabletop.views.delete_roster',
            'pk':'id',
        }
    ),
    url(r'^unsubscribe/(?P<obj_id>\d+)/approve/$','approve_action',
        {
            'message': _('Do you realy want to unsubscribe this site object?'),
            'action_function': 'apps.core.views.delete_subscription',
            'pk': 'id',
        },
    ),
    url(r'^reports/delete/(?P<obj_id>\d+)/approve/$','approve_action',
        {
            'message': _('Do you realy want to delete this battle report?'),
            'action_function': 'apps.tabletop.views.delete_battle_report',
            'pk': 'id',
        }
    ),
    url(r'^password/restored/$', direct_to_template,
        {'template': 'static/password_restored.html'},
        name='password-restored'),
    url(r'^password/restore/initiated/$', direct_to_template,
        {'template': 'static/password_restore_initiated.html'},
        name='password-restore-initiated'),
    url('^unsubscribe/(?P<id>\d+)/(?P<action>(approve|force))/$','delete_subscription',
        name='unsubscribe'),
    url('^db/css/$','db_css',
        name='css-db'),
    url('^db/css/edit/$','add_edit_css',
        name='css-edit'),
    url('^ipaddress/$','get_ip_address',
        name='ip-get-address'),
    url('^permission/denied/$', direct_to_template,
        {'template': 'static/permission_denied.html'},
        name='permission-denied'),
    url('^currently/unavailable/$', direct_to_template,
        {'template': 'static/currently_unavailable.html'},
        name='currently-unavailable'),
    url('^raise/500/$', 'raise_500', name='raise-500'),
    url('^mywot581220ae922fc400475a.html$', direct_to_template,
        {'template': 'static/mywot581220ae922fc400475a.html'},
        name='wot_verification'),
    url('^robots.txt$', 'robots',
       name='url_robots'),
)
