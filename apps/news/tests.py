# coding: utf-8
from django.test import TestCase

from apps.core.tests import TestHelperMixin
from apps.news.models import (
    News, Event, EventWatch,
    EVENT_TYPE_CHOICES
)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
User = get_user_model()

from django.core.urlresolvers import reverse

from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context, Template
from django.utils.unittest import skipIf


from datetime import datetime, timedelta


class BenchmarkTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
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
            url = reverse('news:index')
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
    @skipIf(True, 'broken mark for deletion')
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

    @skipIf(True, 'broken mark for deletion')
    def test_cache_key_prefix(self):
        self.assertEqual(settings.CACHES['default']['KEY_PREFIX'], 'tests')

    @skipIf(True, 'broken mark for deletion')
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

    # only change_event, add_event perms could allow to make crud
    # operations
    def test_event_create(self, role='admin'):
        self.login(role)
        url = reverse('news:event-create')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        count = Event.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.proceed_form_errors(response.context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), count + 1)

    def test_event_create_failure(self):
        url = reverse('news:event-create')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        count = Event.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.proceed_form_errors(response.context)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Event.objects.count(), count)


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

    @skipIf(True, 'broken mark for deletion')
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

    @skipIf(True, 'broken mark for deletion')
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