# coding: utf-8
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from apps.news.models import News


class NewsEntries(Feed):
    title = 'WarMist Lastest News'
    link = '/news/'
    description = "The lastes news"
    title_template = 'feeds/news/newsentries_title.html'
    description_template = 'feeds/news/newsentries_description.html'
    
    def item_link(self, obj):
        link = obj.get_absolute_url()
        return link

    @staticmethod
    def items():
        return News.objects.order_by('-date')[:20]


class AtomNewsEntries(NewsEntries):
    feed_type = Atom1Feed
    title_template = 'feeds/news/news_atom_title.html'
    description_template = 'feeds/news/news_atom_description.html'


feeds = {
    'news': NewsEntries,
    'news_atom': AtomNewsEntries,
}
