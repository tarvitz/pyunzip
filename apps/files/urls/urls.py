from django.conf.urls import *
from django.contrib.auth.decorators import login_required

from apps.core.shortcuts import direct_to_template
from apps.files import views

urlpatterns = patterns(
    'apps.files.views',
    url(r'^replays/$', 'show_replays',
        name='replays-index'),
    url(r'^replays/category/(?P<type>\w+)/$', 'show_categories', name='replay-categories'),
    #(r'^replays/upload/$', 'choose_game_to_upload'),
    url(r'^replays/upload/$', 'upload_replay',
        name='replay-upload'),
    url(r'^replays/(?P<number>\d+)/delete/(?P<approve>(approve|force))/$','purge_replay'),
    #(r'^replays/upload/(?P<game>\w+)/$', 'upload_replay'),
    url(r'^replays/edit/(?P<id>\d+)/$','edit_replay'),

    url(r'^replays/(?P<id>\d+)/(?P<idx>\d+)/$', 'return_replay_from_pack', name='replay-from-pack'), #returns replay from zipped filepack
    url(r'^replays/(?P<id>\d+)/(?P<idx>\d+)/(?P<compress>(plain|zip|bz2))/$', 'return_replay_from_pack',
        name='replay-from-pack'), #returns replay from zipped filepack

    url(r'^galleries/$', views.GalleryListView.as_view(), name='galleries'),
    url(r'^galleries/(?P<pk>\d+)/$', views.GalleryListView.as_view(),
        name='galleries'),

    url(r'^gallery/exists/$', direct_to_template,
        {'template': 'gallery/exists.html'}),

    url(r'^gallery/created/$', direct_to_template,
        {'template': 'gallery/created.html'}),
    url('^galleries/images/(?P<pk>\d+)/$',
        views.GalleryImageDetailView.as_view(), name='image'),
    url(r'^galleries/images/upload/$',
        login_required(views.GalleryImageCreateView.as_view()),
        name='image-upload'),
    url(r'^galleries/images/(?P<pk>\d+)/delete/$',
        login_required(views.GalleryImageDeleteView.as_view()),
        name='image-delete'),
    url(r'^i/(?P<alias>[\w\d_]+)/$', 'show_raw_image', 
        name='url_show_raw_image'),
    url(r'^ti/(?P<alias>[\w\d_]+)/$', 'show_raw_image', {'thumbnail': True},
        name='url_show_raw_image'),
    url(r'^images/(?P<pk>\d+)/edit/$',
        login_required(views.GalleryImageUpdateView.as_view()),
        name='image-edit'),
    url(r'^files/upload/new/$', 'file_upload', name='file-upload'),

    # todo: refactor
    url(r'^users/files/$', 'files', name='files'),
    url(r'^users/files/(?P<pk>\d+)/delete/$', 'file_delete', name='file-delete')
)

