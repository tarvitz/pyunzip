from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.files.views',
    #(r'^upload/file/$', 'upload_file'),
    url(r'^upload/file/$', 'upload_file',
        name='file-upload'),
    url(r'^replays/$', 'show_replays',
        name='replays-index'),
    url(r'^replays/search/$', 'search_replay', name='replay-search'),
    url(r'^replays/category/(?P<type>\w+)/$', 'show_categories', name='replay-categories'),
    #(r'^replays/upload/$', 'choose_game_to_upload'),
    url(r'^replays/upload/$', 'upload_replay',
        name='replay-upload'),
    url(r'^replays/(?P<number>\d+)/delete/(?P<approve>(approve|force))/$','purge_replay'),
    #(r'^replays/upload/(?P<game>\w+)/$', 'upload_replay'),
    url(r'^replays/edit/(?P<id>\d+)/$','edit_replay'),
    url('^replays/author/(?P<nickname>[\w\s]+)/$','replays_by_author',
        name='replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/$','replays_by_author',
        name='replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/$','replays_by_author',
        name='replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/(?P<version>[\w\s]+)/$','replays_by_author',
        name='replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\d\s.]+)/$','replays_by_author',
        name='replays'),
    url('^replays/(?P<number>\d+)/$','show_replay',{'object_model':'files.replay'},
        name='url_show_replay'), #WTF????
    url(r'^replays/(?P<id>\d+)/(?P<idx>\d+)/$', 'return_replay_from_pack', name='replay-from-pack'), #returns replay from zipped filepack
    url(r'^replays/(?P<id>\d+)/(?P<idx>\d+)/(?P<compress>(plain|zip|bz2))/$', 'return_replay_from_pack',
        name='replay-from-pack'), #returns replay from zipped filepack
    url(r'^replays/all/$', 'all_replays', name='replays'),
    url(r'^replays/all/(?P<gametype>\d+)/$', 'all_replays', name='replays'),
    url(r'^replays/(?P<type>\w+)/$', 'all_replays', name='replays'),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/duel/$', 'category_replays', {'type': 1}),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/team/$', 'category_replays', {'type': 2}),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/nonstd/$', 'category_replays', {'type': 0}),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/duel/$', 'category_replays', {'type': 1}),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/team/$', 'category_replays', {'type': 2}),
    url(r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/nonstd/$', 'category_replays', {'type': 0}),
    url(r'^replays/all/duel/$', 'category_replays', {'type':1}),
    url(r'^replays/all/nonstd/$', 'category_replays', {'type':0}),
    url(r'^replays/all/team/$', 'category_replays', {'type':2}),
    url(r'^replays/(?P<gametype>\w+)/duel/$', 'category_replays', {'type': 1}),
    url(r'^replays/(?P<gametype>\w+)/team/$', 'category_replays', {'type': 2}),
    url(r'^replays/(?P<gametype>\w+)/nonstd/$', 'category_replays', {'type': 0}),
    #
    url(r'^replays/(?P<type>\w+)/(?P<version>[\w\s]+)/$', 'all_replays'),
    url(r'^replays/(?P<type>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/$', 'all_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<version>\w+)/(?P<patch>[\w\s.]+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<version>\w+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<type>\d+)/$', 'all_'),
    #
    url(r'^gallery/$', 'show_all_images',
        name='galleries'),
    url(r'^gallery/(?P<id>\d+)/$', 'show_all_images', name='gallery'),
    #(r'^gallery/create/$', 'create_gallery'),
    url(r'^gallery/exists/$', direct_to_template,
        {'template': 'gallery/exists.html'}),
    #(r'^gallery/(?P<gallery>\d+)/$', 'show_gallery'),
    url(r'^gallery/created/$', direct_to_template,
        {'template': 'gallery/created.html'}),
    #deprecated, cleanse
    #(r'^gallery/upload/$', 'upload_image'),
    url(r'^gallery/upload/$', 'upload_image',
        name='image-upload'),
    url(r'^gallery/(?P<gallery_name>[\w\s]+)/$', 'show_gallery'),
    #can delete both way: via url address and delete_function:
    url('^gallery/image/(?P<id>\d+)/(?P<action>delete)/approve/$','action_image',
        name='image-delete'),
    url('^gallery/image/(?P<id>\d+)/(?P<action>delete)/$','action_image',
        name='image-delete-force'),
    url(r'^gallery/image/(?P<number>\d+)/$', 'show_image', {'object_model':'files.image'},
        name='image'),
    url(r'^image/(?P<number>\d+)/$', 'show_image',{'object_model':'files.image'},
        name='url_show_image'), #alias
    url(r'^i/(?P<alias>[\w\d_]+)/$', 'show_raw_image', 
        name='url_show_raw_image'),
    url(r'^ti/(?P<alias>[\w\d_]+)/$', 'show_raw_image', {'thumbnail': True},
        name='url_show_raw_image'),
    url(r'^image/edit/(?P<id>\d+)/$', 'action_image', {'action': 'edit'},
        name='image-edit'),
    url(r'^files/$', 'show_files',
        name='files-index'),
    #(r'^test/upload_replay/$', 'upload_replay'),
    #obsolete #todo: cleanse it all!
    #(r'^test/upload_image/$', 'upload_image'),
    #(r'^test/make_fake_attachments/$', 'make_fake_attachments'),
    #(r'^test/make_fake_files/replays/$', 'make_fake_files', {'model':'files.replay','field':'replay'}),
    #(r'^test/make_fake_files/files/$', 'make_fake_files', {'model':'files.file','field':'file'}),
    #(r'^test/make_fake_files/images/$', 'make_fake_files', {'model':'files.image','field':'image'}),
    #(r'^test/make_fake_files/thumbnails/$', 'make_fake_files', {'model':'files.image','field':'thumbnail'}),
    url(r'^files/upload/new/$', 'file_upload', name='file-upload'),
    url(r'^test/files/upload/$', 'test_file_upload', name='test-file-upload'),
    url(r'^users/files/$', 'files', name='files'),
    url(r'^users/files/(?P<pk>\d+)/delete/$', 'file_delete', name='file-delete')
)

