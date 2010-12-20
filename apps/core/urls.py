from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.core.views',
    (r'^search/$', 'search'),
    (r'^search/(?P<model>\w+)/$', 'search_model'),
    (r'^settings/$','user_settings'),
    (r'^settings/store/(?P<key>[\w_]+)/(?P<value>\w+)/$','set_settings'),
    (r'^subscription/$','view_subscription'),
    (r'^unsubscribe/(?P<id>\d+)/$','delete_subscription'),
    url('^show/comments/(?P<model>[\w\s]+)/(?P<object_pk>[\w\s]+)/$','show_comments',
        name='show_comments'),
    (r'^gallery/image/(?P<obj_id>\d+)/delete/approve/$', 'approve_action',
        {
        'message': _('Do you realy want to delete this image?'),
        #'url': '/gallery/image/\%s/delete/',
        'action_function': 'apps.files.views.action_image',
        'action_type': 'delete',
        },
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

)
