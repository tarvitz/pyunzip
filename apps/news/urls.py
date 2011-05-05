from django.conf.urls.defaults import *
from apps.news import views

urlpatterns = patterns('apps.news.views', 
    (r'^$','news'),
    (r'^news/(?P<approved>(unapproved|approved))/$', 'news'), #this is somekind of brainfuck!
    url(r'^news/$', views.news, name='url_news'),
    (r'^news/$', 'news'),
    (r'^news/archived/$','archived_news'),
    (r'^archived/article/(?P<id>\d+)/$','show_archived_article'),
    (r'^news/(?P<category>[\w\s]+)/$', 'news'),
    #(r'^news/(?P<page>)/$', 'news' ),
    (r'^news/article/(?P<number>\d+)/$', 'show_article',{'object_model':'news.news'}),
    (r'^article/(?P<number>\d+)/$', 'show_article',{'object_model':'news.news'}),
    (r'^article/add/$', 'add_article'),
    (r'^article/edit/(?P<id>\d+)/$','add_article', {'edit_flag':'True'}),
    (r'^article/(?P<id>\d+)/(?P<action>(approve|unapprove|delete))/$', 'article_action'),
    url(r'^article/(?P<id>\d+)/delete/$', 'article_action', {'action': 'delete'},
        name='url_article_delete'),
    #moved to apps.core.urls and apps.core.views
    #url('^comment/edit/(?P<id>\d+)/$', 'edit_comment',
    #    name='url_edit_comment'),
    url('^comment/(?P<id>\d+)/(?P<flag>(delete|restore))/$', 'del_restore_comment',
        name='url_del_restore_comment'), #do delete,restore
    #here is a half-a-fake function, that will be completed via core.views.approve_action, see core.urls :)
    url('^comment/(?P<id>\d+)/purge/(?P<approve>(approve|force))/$','purge_comment',
        name='url_purge_comment'),
    #ajax integration
    (r'^comment/(?P<id>\d+)/update/$', 'edit_comment_ajax'),
    (r'^comment/(?P<id>\d+)/get/$', 'get_comment'), #json format reply
    (r'^comment/(?P<id>\d+)/get/raw/$', 'get_comment', {'raw':True}), #json format reply
    url(r'^sphinx/news/$', 'sphinx_news',name='url_sphinx_news'),
)
