from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _
from apps.core.shortcuts import direct_to_template

urlpatterns = patterns('apps.core.views',
    #(r'^search/$', 'search'),
    #(r'^search/(?P<model>\w+)/$', 'search_model'),
    url(r'^search/(?P<model>\w+)/$', 'sphinx_search_model',
        name='url_sph_search_model'),
    url(r'^search/$', 'sphinx_search',
        name='url_sph_search'),
    (r'^settings/$','user_settings'),
    (r'^settings/store/(?P<key>[\w_]+)/(?P<value>\w+)/$','set_settings'),
    url(r'^subscription/$','view_subscription',
        name='url_view_subscription'),
    (r'^unsubscribe/(?P<id>\d+)/$','delete_subscription'),
    url('^add/comment/$', 'save_comment', name='url_save_comment'),
    url('^edit/comment/(?P<id>\d+)/','edit_comment',name='url_edit_comment'),
    url('^show/comments/(?P<model>[\w\s]+)/(?P<object_pk>[\w\s]+)/$','show_comments',
        name='show_comments'),
    url('^upload/get/progress/$','uploader_progress',name='url_upload_progress'),
    url('^xhr/upload/(?P<app_n_model>[\w\.]+)/$', 'upload_file',name='url_progress_uploader'),
    #deprecated, cleanse
    url('^upload/(?P<app_n_model>[\w\.]+)/(?P<filefield>\w+)/$', 'upload_file',name='url_progress_uploader'),
    (r'^gallery/image/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
        'message': _('Do you realy want to delete this image?'),
        #'url': '/gallery/image/\%s/delete/',
        'action_function': 'apps.files.views.action_image',
        'action_type': 'delete',
        },
    ),
    url(r'article/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
        'action_type': 'delete',
        'message': _('Do you realy want to delete this article?'),
        'action_function': 'apps.news.views.article_action',
        }, name='url_article_delete_approve',
    ),
    (r'^comment/(?P<obj_id>\d+)/purge/approve/$', 'approve_action',
        {
          #'url': '/comment/\%s/purge/',
          'message': _('Do you realy want to purge this comment? O_O.. realy?'),
          'action_function': 'apps.news.views.purge_comment',
        }
    ), #ask to purge
    (r'^replays/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to purge this replay?'),
            'action_function': 'apps.files.views.do_purge_replay',
        }
    ),
    (r'^pm/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to delete this comment?'),
            'action_function': 'apps.wh.views.delete_pm',
            'pk': 'pm_id',
        },
    ),
    (r'^roster/delete/(?P<obj_id>\d+)/approve/$', 'approve_action',
        {
            'message': _('Do you realy want to delete this roster?'),
            'action_function': 'apps.tabletop.views.delete_roster',
            'pk':'id',
        }
    ),
    (r'^unsubscribe/(?P<obj_id>\d+)/approve/$','approve_action',
        {
            'message': _('Do you realy want to unsubscribe this site object?'),
            'action_function': 'apps.core.views.delete_subscription',
            'pk': 'id',
        }
    ),
    (r'^reports/delete/(?P<obj_id>\d+)/approve/$','approve_action',
        {
            'message': _('Do you realy want to delete this battle report?'),
            'action_function': 'apps.tabletop.views.delete_battle_report',
            'pk': 'id',
        }
    ),
    url('^unsubscribe/(?P<id>\d+)/(?P<action>(approve|force))/$','delete_subscription',
        name='url_unsubscribe'),
    url('^db/css/$','db_css',
        name='url_db_css'),
    url('^db/css/edit/$','add_edit_css',
        name='url_add_edit_css'),
    url('^ipaddress/$','get_ip_address',
        name='url_get_ip_address'),
    url('^permission/denied/$', direct_to_template,
        {'template': 'static/permission_denied.html'},
        name='url_permission_denied'),
    url('^currently/unavailable/$', direct_to_template,
        {'template': 'static/currently_unavailable.html'},
        name='url_currently_unavailable'),
    url('^mywot581220ae922fc400475a.html$', direct_to_template,
        {'template': 'static/mywot581220ae922fc400475a.html'},
        name='wot_verification'),
    url('^robots.txt$', 'robots',
       name='url_robots'),
)
