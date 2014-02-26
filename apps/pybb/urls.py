from django.conf.urls import *

from apps.pybb import views
from apps.pybb.feeds import LastPosts, LastTopics

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
}
urlpatterns = patterns(
    url('^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name='pybb_feed'),

)
urlpatterns += patterns('',
    # Misc
    url('^$', views.index, name='pybb_index'),
    url('^category/(?P<category_id>\d+)/$', views.show_category, name='pybb_category'),
    url('^forum/(?P<forum_id>\d+)/$', views.show_forum, name='pybb_forum'),
        # User
    url('^user/(?P<username>.*)/$', views.user, name='pybb_profile'),
    url('^profile/edit/$', views.edit_profile, name='pybb_edit_profile'),
    url('^users/$', views.users, name='pybb_users'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic, name='pybb_topic'),
    url('^topics/(?P<pk>\d+)/posts/$', views.PostListView.as_view(),
        name='posts'),
    url('^forum/(?P<forum_id>\d+)/topic/add/$', views.add_post,
        {'topic_id': None}, name='pybb_add_topic'),
    url('^topic/(?P<topic_id>\d+)/stick/$', views.stick_topic, name='pybb_stick_topic'),
    url('^topic/(?P<topic_id>\d+)/unstick/$', views.unstick_topic, name='pybb_unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/close/$', views.close_topic, name='pybb_close_topic'),
    url('^topic/(?P<topic_id>\d+)/open/$', views.open_topic, name='pybb_open_topic'),

    # Post
    url('^topic/(?P<topic_id>\d+)/post/add/$', views.add_post,
        {'forum_id': None}, name='pybb_add_post'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='pybb_post'),
    url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='pybb_edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', views.delete_post, name='pybb_delete_post'),

    # Subscription
    url('^subscription/topic/(?P<topic_id>\d+)/delete/$', views.delete_subscription, name='pybb_delete_subscription'),
    url('^subscription/topic/(?P<topic_id>\d+)/add/$', views.add_subscription, name='pybb_add_subscription'),

    # Private messages
    url('^pm/new/$', views.create_pm, name='pybb_create_pm'),
    url('^pm/outbox/$', views.pm_outbox, name='pybb_pm_outbox'),
    url('^pm/inbox/$', views.pm_inbox, name='pybb_pm_inbox'),
    url('^pm/show/(?P<pm_id>\d+)/$', views.show_pm, name='pybb_show_pm'),
    url('^themes/(?P<theme>[\w\d]+)/switch/$', views.switch_theme, name='pybb_switch_theme'),
    # additional possibilites, Polls
    url('^topic/(?P<pk>\d+)/poll/add/$', views.ManagePollView.as_view(),
        name='pybb_poll_add'),
    url('^poll/(?P<pk>\d+)/update/$', views.ManagePollView.as_view(),
        {'update': True},
        name='pybb_poll_update'),
    url('^poll/(?P<pk>\d+)/delete/$', views.ManagePollView.as_view(),
        {'delete': True},
        name='pybb_poll_delete'),
    url('^poll/(?P<pk>\d+)/configure/$', views.ConfigurePollView.as_view(),
        name='pybb_poll_configure'),
    url('^poll/(?P<pk>\d+)/vote/$', views.PollVoteView.as_view(),
        name='pybb_poll_vote'),
    #url('^topic/(?P<pk>\d+)/poll/add/step/(?P<step>.+)/$',
    #    views.add_poll_wizard, name='pybb_poll_add'),
)
