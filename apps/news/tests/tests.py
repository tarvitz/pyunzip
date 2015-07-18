# coding: utf-8
import logging
from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse

from apps.accounts.models import User
from apps.core.tests import TestHelperMixin
from apps.news.models import (
    Event, EventWatch, EVENT_TYPE_CHOICES
)

import allure
from allure.constants import Severity


logger = logging.getLogger(__file__)


@allure.feature('Benchmark: News')
class BenchmarkTest(TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_news_categories.json',
    ]

    def setUp(self):
        from apps.news import views
        self.views = views
        logger.info("Run benchmarking tests for news")

    def tearDown(self):
        logger.info("End of benchmarking tests for news")

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_news(self):
        for user in ['user', 'admin', None]:
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            results = []
            url = reverse('news:news')
            for i in range(1, 10):
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
            logger.info(
                "Benchmarking %(user)s %(url)s: min: %(min)s, "
                "max: %(max)s, avg: %(avg)s" % msg
            )


@allure.feature('General: Events')
class EventTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
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
    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
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

    @allure.story('create')
    @allure.severity(Severity.NORMAL)
    def test_event_create_failure(self):
        url = reverse('news:event-create')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        count = Event.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.proceed_form_errors(response.context)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Event.objects.count(), count)


@allure.feature('General: Event Watches')
class EventWatchTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_event_places.json',
        'load_events.json'
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

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_event_watched(self):
        """
        common test for watched event by user watch event action,
        event watch instance should be registered
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

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_event_watched_is_finished(self):
        """
        common test for watched event by user event action if event is
        finished, event watch instance shouldn't be registered
        """
        self.login('user')
        User.objects.get(username='user')
        event = Event.objects.filter(is_finished=True)[0]
        count = EventWatch.objects.count()
        self.assertEqual(count, 0)

        response = self.client.get(event.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EventWatch.objects.count(), count)
