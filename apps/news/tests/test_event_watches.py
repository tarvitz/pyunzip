# coding: utf-8
from datetime import datetime, timedelta
from django.test import TestCase

from apps.accounts.models import User
from apps.core.tests import TestHelperMixin
from apps.news.models import (
    Event, EventWatch
)

import allure
from allure.constants import Severity


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
