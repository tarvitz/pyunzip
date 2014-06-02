# coding: utf-8
#from django.utils import unittest
from django.test import TestCase
#import unittest
#from django.test.client import RequestFactory, Client
from apps.core.tests import TestHelperMixin
from apps.news.models import (
    Category, News, Event, EventWatch,
    EVENT_TYPE_CHOICES
)
try:
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
#from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse
from apps.core.models import Announcement
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_object_or_None
#from django.db import connections
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context, Template
from apps.core.helpers import paginate

from datetime import datetime, timedelta


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json',
    ]

    def setUp(self):
        self.urls_void = [
            "/news/",
            '/news/archived/',
            '/markup/preview/',
            '/article/created/'
        ]
        self.urls_registered = [
            '/article/add/',  # 302
            "/news/user/",  # 302
        ]
        self.urls_302 = [

        ]
        self.urls_params = [
            reverse('news:news', args=('testing',)),
            reverse('news:article', args=(1,)),
        ]

    def test_urls_params(self):
        messages = []
        for user in ('user', 'admin', None):
            if user:
                self.client.login(username=user, password='123456')
            else:
                self.client.logout()
            for url in self.urls_params:
                response = self.client.get(url)
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({'url': url, 'user': user, 'err': err})
        if messages:
            for msg in messages:
                print "Got error in (%s): %s, with %s" % (
                    msg['user'], msg['url'], msg['err']
                )
            raise AssertionError

    def test_urls_anonymous(self):
        self.client.logout()
        messages = []
        for url in self.urls_registered:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as err:
                messages.append({'url': url, 'err': err})
        if messages:
            for msg in messages:
                print "URL: %(url)s failed with: %(err)s" % msg
            raise AssertionError

    def test_urls_generic(self):
        messages = []

        for url in self.urls_void:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as err:
                messages.append({'err': err, 'url': url})
        if messages:
            for msg in messages:
                print "URL: %(url)s failed with: %(err)s" % msg
            print "=" * 10
            raise AssertionError
        messages = []
        for url in self.urls_302:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as err:
                messages.append({'err': err, 'url': url})
        for msg in messages:
            print "URL: %(url)s failed with: %(err)s" % msg
        if messages:
            print "=" * 10
            raise AssertionError

    def test_user_login(self):
        pass

    def test_urls_user(self):
        loggined = self.client.login(username='user', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()

    def test_urls_admin(self):
        loggined = self.client.login(username='admin', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()

    def test_news_post_anonymous(self):
        self.client.logout()
        category = Category.objects.all()[0]
        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 1',
            'syntax': 'textile',
            'url': '',
        }
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        self.assertNotEqual(count + 1, new_count)

    def test_news_post_user(self):
        # user posts article without approval

        self.client.login(username='user', password='123456')
        user = User.objects.get(username='user')

        category = Category.objects.all()[0]
        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 1',
            'syntax': 'textile',
            'url': '',
        }
        url = reverse('news:article-add')
        response = self.client.post(
            url, post, follow=True
        )
        #print "\ntesting: %s\n" % url

        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        self.assertEqual(count + 1, new_count)
        article = News.objects.order_by('-id')[0]

        post.update({
            'category': category,
            'author': user.username
        })
        for (key, value) in post.items():
            self.assertEqual(getattr(article, key), value)
        self.assertEqual(article.approved, False)

        ct = ContentType.objects.get(
            app_label=article._meta.app_label,
            model=article._meta.module_name
        )

        announcement = Announcement.objects.filter(
            object_pk=article.pk, content_type=ct
        )
        self.assertEqual(len(announcement), 1)

    def test_news_post_super_user(self):
        # superuser posts article with approval
        username = 'admin'
        logged = self.client.login(username=username, password='123456')
        self.assertEqual(logged, True)
        user = User.objects.get(username=username)
        category = Category.objects.all()[0]

        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 2',
            'syntax': 'textile',
            'url': '',
            'approved': True
        }
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        self.assertEqual(count + 1, new_count)
        article = News.objects.order_by('-id')[0]

        post.update({
            'category': category,
            'author': user.username
        })
        messages = []
        for (key, value) in post.items():
            try:
                self.assertEqual(getattr(article, key), value)
            except AssertionError as err:
                messages.append({'err': err, 'key': key})
        if messages:
            for msg in messages:
                print "Got assertion error in %(key)s with %(err)s" % msg
            raise AssertionError
        self.assertEqual(article.approved, True)

        # testing for if not approved
        post.update({
            'approved': False,
            'category': category.id,
            'author': ''
        })
        news_count = News.objects.count()
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(news_count + 1, News.objects.count())
        article = News.objects.order_by('-id')[0]
        messages = []

        post.update({
            'approved': False,
            'category': category,
            'author': user.username
        })
        for (key, value) in post.items():
            try:
                self.assertEqual(getattr(article, key), value)
            except AssertionError as err:
                messages.append({'err': err, 'key': key})
        if messages:
            for msg in messages:
                print "Got assertion error in %(key)s with %(err)s" % msg
            raise AssertionError
        self.assertEqual(article.approved, False)

    def test_news_user_actions(self):
        # user can not approve or disapprove articles

        username = 'user'
        self.client.login(username=username, password='123456')
        count = News.objects.count()
        category = Category.objects.all()[0]
        post = {
            'title': u'Заголовок', 'author': '',
            # blank means poster user
            'category': category.id, 'content': u'Новость 2',
            'syntax': 'textile', 'url': '',
            'approved': True
        }
        response = self.client.post(reverse('news:article-add'), post, follow=True)
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        article = News.objects.order_by('-id')[0]
        self.assertEqual(count + 1, new_count)
        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'approve'))
        )
        self.assertEqual(response.status_code, 404)
        article = News.objects.get(pk=article.pk)
        self.assertNotEqual(article.approved, True)
        article.approved = True
        article.save()

        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'unapprove'))
        )
        self.assertEqual(response.status_code, 404)
        article = News.objects.get(pk=article.pk)
        self.assertNotEqual(article.approved, False)

    def test_admin_user_actions(self):
        # admin can approve or disapprove articles

        username = 'admin'
        self.client.login(username=username, password='123456')
        count = News.objects.count()
        category = Category.objects.all()[0]
        post = {
            'title': u'Заголовок', 'author': '',
            # blank means poster user
            'category': category.id, 'content': u'Новость 2',
            'syntax': 'textile', 'url': '',
        }
        response = self.client.post(reverse('news:article-add'), post, follow=True)
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        article = News.objects.order_by('-id')[0]
        self.assertEqual(count + 1, new_count)
        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'approve')),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        self.assertEqual(article.approved, True)
        article.approved = True
        article.save()

        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'unapprove')),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        self.assertEqual(article.approved, False)

    def test_news_edit(self):
        # user can not edit articles that do not belong to him
        # admin can edit any article
        # anonymous can not edit articles at all
        self.client.logout()
        article = News.objects.exclude(owner__username='user')[0]
        edit = {
            'title': u'Новый заголовок',
            'content': u'Новый контент',
            #'author': article.author,  # blank means poster user
            #'syntax': article.syntax,
            #'url': article.url,
        }
        post = dict(category=article.category.id, **edit)
        url = reverse('news:article-edit', args=(article.id, ))
        # anonymous can not edit any news
        self.client.post(url, post, follow=True)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # user can not edit news not of his own
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # admin can edit any news
        logged_in = self.client.login(username='admin', password='123456')
        self.assertEqual(logged_in, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertEqual(getattr(article, key), value)

        # reset data for user checks
        article.title = 'Radom data here'
        article.content = 'Random content here'
        article.save()

        # user can edit his news but only if their are unapproved!
        self.client.login(username='user', password='123456')
        article = News.objects.filter(owner__username='user', approved=True)[0]
        url = reverse('news:article-edit', args=(article.id,))
        post = dict(category=article.category.id, **edit)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 404)

        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # user can edit his news only if their are unapproved
        article = News.objects.filter(owner__username='user', approved=False)[0]
        url = reverse('news:article-edit', args=(article.pk, ))
        post = dict(category=article.category.id, **edit)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertEqual(getattr(article, key), value)

    def test_article_delete(self):
        # only admin can delete articles
        article = {
            'title': 'deletion',
            'content': 'to delete',
            'syntax': 'textile',
            'author': 'admin',
            'editor': '',
            'category_id': 1,
            'approved': True,
            'owner_id': 1,
        }

        n = News.objects.create(**article)
        # testing deletion with user, no access to delete
        self.client.login(username='user', password='123456')
        url = reverse('news:article-delete', args=(n.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        exists = get_object_or_None(News, pk=n.id)
        self.assertNotEqual(exists, None)

        # deleting by admin
        self.client.login(username='admin', password='123456')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        exists = get_object_or_None(News, pk=n.id)
        self.assertEqual(exists, None)

    def test_article_set_status(self):
        post = {
            'status': 'revision',
            'resend': False,
            'reason': "please make it nice"
        }
        # nobody except admin could set news status
        # testing anonymous
        n = News.objects.filter(approved=False)[0]
        url = reverse('news:article-status-set', args=(n.id, ))
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login required")
        # checking for user
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        n = News.objects.get(id=n.id)
        self.assertNotEqual(n.reason, post['reason'])
        # checking for admin
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        n = News.objects.get(id=n.id)
        self.assertEqual(n.reason, post['reason'])


class BenchmarkTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/production/load_news.json',
    ]

    def setUp(self):
        #self.request = RequestFactory()
        #self.client = Client()
        from apps.news import views
        self.views = views
        print "Run benchmarking tests for news"

    def tearDown(self):
        print "End of benchmarking tests for news"

    def test_news(self):
        for user in ['user', 'admin', None]:
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            results = []
            url = reverse('news:news')
            for i in xrange(1, 10):
                n = datetime.now()
                self.client.get(url)
                offset = datetime.now() - n
                results.append(offset.total_seconds())
            minimum = min(results)
            maximum = max(results)
            avg = sum(results) / len(results)
            msg = {
                'url': url, 'user': user or 'Anonymous',
                'min': minimum, 'max': maximum, 'avg': avg
            }
            print "Benchmarking %(user)s %(url)s: min: %(min)s, max: %(max)s, avg: %(avg)s" % msg


class BenchmarkTemplatesTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/production/load_news.json'
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def benchmark_run(self, run=lambda x: x, runs=10):
        results = []
        for i in xrange(runs):
            n = datetime.now()
            run()
            offset = datetime.now() - n
            results.append(offset.total_seconds())

        print "Got: min: %(min)s, max: %(max)s, avg: %(avg)s" % {
            'min': min(results),
            'max': max(results),
            'avg': sum(results) / len(results)
        }

    def benchmark(self, template, context=None, runs=10):
        results = []
        context = context or {}
        for i in xrange(runs):
            n = datetime.now()
            if isinstance(template, basestring):
                tmpl = Template(template)
            else:
                tmpl = template
            tmpl.render(Context(context))
            offset = datetime.now() - n
            results.append(offset.total_seconds())
        rmin = min(results)
        rmax = max(results)
        avg = sum(results) / len(results)
        print "Got follow timings:\nmin: %(min)s,\nmax: %(max)s,\navg: %(avg)s" % {
            'min': rmin,
            'max': rmax,
            'avg': avg
        }

    def test_news_page_plain(self):
        print "Testing news page without render, only with context processors and stuff"
        template = get_template('news.html')
        url = reverse('wh:login')  # without anything worthless
        response = self.client.get(url)
        context = response.context[0]

        for user in ('admin', 'user', None):
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            print "Testing for '%s': " % user or 'Anonymous'
            self.benchmark(template, context)

    def test_news_page_full(self):
        print "Testing news page with news render, only news fetched"
        from apps.news.views import news
        url = reverse('wh:login')
        template = get_template('news.html')
        for user in ('admin', 'user', None):
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            print "Testing for '%s': " % user or 'Anonymous'
            context = self.client.get(url).context
            news = News.objects.all()
            news = paginate(news, 1, pages=20)
            context = context[0]
            context['news'] = news
            context['page'] = news
            self.benchmark(template, context)


class CacheTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json',
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache_key_prefix(self):
        self.assertEqual(settings.CACHES['default']['KEY_PREFIX'], 'tests')

    def test_news_cache(self):
        keys = ['admin', 'everyone', 'everyone']
        users = ['admin', 'user', None]
        messages = []

        for (key, user) in zip(keys, users):
            cache.delete('news:all:%s' % key)
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
                u = User.objects.get(username=user)
            else:
                self.client.logout()
                u = AnonymousUser()
            try:
                cache_key = 'news:all:%s' % key
                self.assertEqual(cache.get('news:all:%s' % key), None)
                self.client.get('/')
                caches = list(cache.get(cache_key).order_by('-date'))
                qset = Q()
                if not u.has_perm('news.can_edit'):
                    qset = Q(approved=True)

                news = list(News.objects.filter(qset).order_by('-date'))

                self.assertListEqual(
                    caches or [],
                    news or [None, ]
                )
                print "%s passes" % user
            except AssertionError as err:
                messages.append({
                    'user': user,
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print "Got %(err)s with '%(user)s' in %(key)s" % msg
            raise AssertionError


class EventTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]
    post = {
        'title': u'Новое событие',
        'content': u'Текст содержания',
        'date_start': datetime.now(),
        'date_end': datetime.now() + timedelta(hours=24),
        'type': EVENT_TYPE_CHOICES[0][0]
    }

    def setUp(self):
        pass

    def test_event_create(self):
        self.login('user')
        url = reverse('news:event-create')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        count = Event.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), count + 1)


class EventWatchTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json'
    ]

    def setUp(self):
        # process events and reset date_start, date_end for
        # further test runs corrections
        now = datetime.now()
        for event in Event.objects.all():
            offset = now - event.date_start
            event.date_start += timedelta(seconds=offset.seconds)
            event.date_end += timedelta(seconds=offset.seconds)
            event.save()

    def test_event_watched(self):
        """
        common test for watched event by user watch event action,
        eventwatch instance should be registered
        """
        self.login('user')
        user = User.objects.get(username='user')
        event = Event.objects.exclude(is_finished=True)[0]
        count = EventWatch.objects.count()
        self.assertEqual(count, 0)

        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EventWatch.objects.count(), count + 1)
        event_watch = EventWatch.objects.latest('pk')
        self.assertEqual(event_watch.user, user)
        self.assertEqual(event_watch.event, event)

    def test_event_watched_is_finished(self):
        """
        common test for wached event by user event action if event is finished,
        eventwatch instance shouldn't be registered
        """
        self.login('user')
        user = User.objects.get(username='user')
        event = Event.objects.filter(is_finished=True)[0]
        count = EventWatch.objects.count()
        self.assertEqual(count, 0)

        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EventWatch.objects.count(), count)