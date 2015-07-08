from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from apps.comments import views

urlpatterns = patterns(
    '',
    url(r'^comments/(?P<pk>\d+)/$', views.CommentDetailView.as_view(),
        name='comment-detail'),
    url(r'^comments/add/$', login_required(views.CommentCreateView.as_view()),
        name='comment-add'),
    url(r'^comments/(?P<pk>\d+)/update/$',
        login_required(views.CommentUpdateView.as_view()),
        name='comment-update'),
    url(r'^comments/(?P<content_type>\d+)/(?P<object_pk>\d+)/subscribe/$',
        login_required(views.SubscribeCommentWatchView.as_view()),
        name='subscription-add'),
    url(r'^subscriptions/$',
        login_required(views.CommentWatchListView.as_view()),
        name='subscriptions'),
    url(r'^subscriptions/(?P<pk>\d+)/remove/$',
        login_required(views.RemoveSubscriptionView.as_view()),
        name='subscription-remove')
)
