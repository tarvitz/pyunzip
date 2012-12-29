from django.conf.urls.defaults import *
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed,Rss201rev2Feed
from django.core.exceptions import ObjectDoesNotExist
from apps.blogs.models import Post

class PostEntries(Feed):
    title = 'WarMist Developer\'s Blog Posts'
    link = '/devblog/'
    description = "The lastes developers posts"
    title_template = 'feeds/blogs/post_title.html'
    description_template = 'feeds/blogs/post_description.html'
    
    def item_link(self,obj):
        link = obj.get_absolute_url() #"/news/article/%s" % obj.id
        return link

    def items(self):
        return Post.objects.order_by('-date')[:20]

class AtomPostEntries(PostEntries):
    feed_type = Atom1Feed
    title_template = 'feeds/blogs/post_atom_title.html'
    description_template = 'feeds/blogs/post_atom_description.html'

