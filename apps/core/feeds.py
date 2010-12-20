from django.conf.urls.defaults import *
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed,Rss201rev2Feed
from django.core.exceptions import ObjectDoesNotExist
from apps.news.models import News
from apps.files.models import Replay,Game
from apps.blogs.feeds import PostEntries,AtomPostEntries
from django.core.urlresolvers import reverse

class NewsEntries(Feed):
    title = 'WarMist Lastest News'
    link = '/news/'
    #link = reverse('apps.news.views.news')# not work :(
    description = "The lastes news"
    title_template = 'feeds/news/newsentries_title.html'
    description_template = 'feeds/news/newsentries_description.html'
    
    def item_link(self,obj):
        #link = "/news/article/%s" % obj.id
        link = obj.get_absolute_url()
        return link

    def items(self):
        return News.objects.order_by('-date')[:20]

class AtomNewsEntries(NewsEntries):
    feed_type = Atom1Feed
    title_template = 'feeds/news/news_atom_title.html'
    description_template = 'feeds/news/news_atom_description.html'

class ReplayEntries(Feed):
    title = 'WarMist Lastest Replays'
    link = '/replays/'
    description = 'The lastest replays'
    title_template = 'feeds/replays/replays_title.html'
    description_template = 'feeds/replays/replays_description.html'
    feed_type = Atom1Feed

    def item_link(self, obj):
        link = "/replays/%s" % obj.id
        return link

    def item_enclosure_url(self,item):
        return '/media/replays/%s/%s' % (item.author.id, item.replay)
    item_enclosure_mime_type = 'octet/stream'
    def item_enclosure_length(self, item):
        return item.replay.size

    def items(self):
        return Replay.objects.order_by('-upload_date')[:20]

class RssReplayEntries(ReplayEntries):
    feed_type = Rss201rev2Feed
    title_template = 'feeds/replays/replays_rss_title.html'
    description_template = 'feeds/replays/replays_rss_description.html'

class ReplaysFromTagEntries(Feed):
    feed_type = Atom1Feed
    title_template = 'feeds/replays/from_tags_title.html'
    description_template = 'feeds/replays/from_tags_description.html'
    link = '/replays/'
    title = 'WarMist the lastest replays'
    def get_object(self, bits):
        #in case of "/feeds/replays/[dow]/[soulstorm]|[duel|team|nonstd]/[1.0]|[duel|team|nonstd]/[duel|team|nonstd]"
        #if len(bits) != 1:
        #    raise ObjectDoesNotExist
        #print bits[0] # /feeds/replays_category/dow -> dow
        return bits

    def item_link(self, obj):
        #TODO: it's better to use reverse here
        return self.get_absolute_url()
        #return '/replays/%s' % obj.id

    def items(self, obj): #obj = self.get_object
        if obj[0] not in 'all':
            replays = Replay.objects.filter(version__game__short_name__exact=obj[0])
        if len(obj) > 1:
            if obj[1] not in ('nonstd','duel','team'):
                replays = replays.filter(version__name__iexact=obj[1])
        if len(obj) > 2:
            if obj[2] not in ('nonstd', 'duel', 'team'):
                replays = replays.filter(version__patch__iexact=obj[2])
        try: 
            obj.index('nonstd')
            replays = replays.filter(type='0')
        except ValueError: pass
        try:
            obj.index('duel')
            replays = replays.filter(type='1')
        except ValueError: pass
        try:
            obj.index('team')
            replays = replays.exclude(type='1').exclude(type='0')
        except ValueError: pass
        return replays.order_by('-upload_date')[:20]
    
    def title(self, bits): #obj = get_obj so its bits
        if len(bits)>0:
            try:
                name = Game.objects.filter(short_name__iexact=bits[0]).values('name')[0]
                fullname = name['name']
            except Game.DoesNotExist:
                fullname = obj[0]
            title = 'WarMist the lastest replays: %s' % fullname
        if len(bits)>1:
            title += ' %s' % bits[1]
        if len(bits)>2:
            title += ' v%s' % bits[2]
        if len(bits)>3:
            title += ' %s' % bits[3]
        if len(bits)<0 or len(bits)>4:
            title = 'WarMist the lastest replays'
        return title

class RssReplaysFromTagEntries(ReplaysFromTagEntries):
    feed_type = Rss201rev2Feed
    title_template = 'feeds/replays/from_tags_rss_title.html'
    description_template = 'feeds/replays/from_tags_rss_description.html'

feeds = {
    'news': NewsEntries,
    'news_atom': AtomNewsEntries,
    'replays': ReplayEntries,
    'replays_rss': RssReplayEntries,
    'replays_category': ReplaysFromTagEntries,
    'replays_category_rss': RssReplaysFromTagEntries,
    'devblog': PostEntries,
    'devblog_atom': AtomPostEntries,
    #'categories': LastestEntriesByCategory,
}

