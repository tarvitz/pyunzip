from django.conf.urls.defaults import *
from apps.core.shortcuts import direct_to_template
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.files.views',
    #(r'^upload/file/$', 'upload_file'),
    url(r'^upload/file/$', 'upload_file',
        name='url_upload_file'),
    (r'^replays/$', 'show_replays'),
    (r'^replays/search/$', 'search_replay'),
    (r'^replays/category/(?P<type>\w+)/$', 'show_categories'),
    (r'^replays/upload/$', 'choose_game_to_upload'),
    (r'^replays/(?P<number>\d+)/delete/(?P<approve>(approve|force))/$','purge_replay'),
    (r'^replays/upload/(?P<game>\w+)/$', 'upload_replay'),
    (r'^replays/edit/(?P<id>\d+)/$','edit_replay'),
    url('^replays/author/(?P<nickname>[\w\s]+)/$','replays_by_author',
        name='url_author_replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/$','replays_by_author',
        name='url_author_replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/$','replays_by_author',
        name='url_author_replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/(?P<version>[\w\s]+)/$','replays_by_author',
        name='url_author_replays'),
    url('^replays/author/(?P<nickname>[\w\s]+)/(?P<game>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\d\s.]+)/$','replays_by_author',
        name='url_author_replays'),
    ('^replays/(?P<number>\d+)/$','show_replay',{'object_model':'files.replay'}),
    (r'^replays/(?P<id>\d+)/(?P<idx>\d+)/$', 'return_replay_from_pack'), #returns replay from zipped filepack
    (r'^replays/(?P<id>\d+)/(?P<idx>\d+)/(?P<compress>(plain|zip|bz2))/$', 'return_replay_from_pack'), #returns replay from zipped filepack
    (r'^replays/all/$', 'all_replays'),
    (r'^replays/all/(?P<gametype>\d+)/$', 'all_replays'),
    (r'^replays/(?P<type>\w+)/$', 'all_replays'),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/duel/$', 'category_replays', {'type': 1}),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/team/$', 'category_replays', {'type': 2}),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/nonstd/$', 'category_replays', {'type': 0}),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/duel/$', 'category_replays', {'type': 1}),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/team/$', 'category_replays', {'type': 2}),
    (r'^replays/(?P<gametype>\w+)/(?P<version>[\w\s]+)/nonstd/$', 'category_replays', {'type': 0}),
    (r'^replays/all/duel/$', 'category_replays', {'type':1}),
    (r'^replays/all/nonstd/$', 'category_replays', {'type':0}),
    (r'^replays/all/team/$', 'category_replays', {'type':2}),
    (r'^replays/(?P<gametype>\w+)/duel/$', 'category_replays', {'type': 1}),
    (r'^replays/(?P<gametype>\w+)/team/$', 'category_replays', {'type': 2}),
    (r'^replays/(?P<gametype>\w+)/nonstd/$', 'category_replays', {'type': 0}),
    #
    (r'^replays/(?P<type>\w+)/(?P<version>[\w\s]+)/$', 'all_replays'),
    (r'^replays/(?P<type>\w+)/(?P<version>[\w\s]+)/(?P<patch>[\w\s.]+)/$', 'all_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<version>\w+)/(?P<patch>[\w\s.]+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<version>\w+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<gametype>\w+)/(?P<type>\d+)/$', 'category_replays'),
    #(r'^replays/(?P<type>\d+)/$', 'all_'),
    #
    (r'^gallery/$', 'show_all_images'),
    (r'^gallery/(?P<id>\d+)/$', 'show_all_images'),
    #(r'^gallery/create/$', 'create_gallery'),
    (r'^gallery/exists/$', direct_to_template,
        {'template': 'gallery/exists.html'}),
    #(r'^gallery/(?P<gallery>\d+)/$', 'show_gallery'),
    (r'^gallery/created/$', direct_to_template,
        {'template': 'gallery/created.html'}),
    (r'^gallery/upload/$', 'upload_image'),
    (r'^gallery/(?P<gallery_name>[\w\s]+)/$', 'show_gallery'),
    #can delete both way: via url address and delete_function:
    url('^gallery/image/(?P<id>\d+)/(?P<action>delete)/approve/$','action_image',
        name='url_delete_image'),
    url('^gallery/image/(?P<id>\d+)/(?P<action>delete)/$','action_image',
        name='url_force_delete_image'),
    (r'^gallery/image/(?P<number>\d+)/$', 'show_image',{'object_model':'files.image'}),
    (r'^image/(?P<number>\d+)/$', 'show_image',{'object_model':'files.image'}), #alias
    url(r'^files/$', 'show_files',
        name='url_show_files'),
    (r'^test/upload_replay/$', 'upload_replay'),
    #(r'^test/upload_image/$', 'upload_image'),
    (r'^test/make_fake_attachments/$', 'make_fake_attachments'),
    (r'^test/make_fake_files/replays/$', 'make_fake_files', {'model':'files.replay','field':'replay'}),
    (r'^test/make_fake_files/files/$', 'make_fake_files', {'model':'files.file','field':'file'}),
    (r'^test/make_fake_files/images/$', 'make_fake_files', {'model':'files.image','field':'image'}),
    (r'^test/make_fake_files/thumbnails/$', 'make_fake_files', {'model':'files.image','field':'thumbnail'}),

)


