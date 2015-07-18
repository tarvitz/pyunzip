# coding: utf-8

from datetime import datetime, timedelta
from django.test import TestCase
from apps.news.cron import EventsMarkFinishedCronJob
from apps.news.models import Event

from apps.core.tests import TestHelperMixin

import allure
from allure.constants import Severity


@allure.feature('Cron: Events')
class TestCronJobs(TestHelperMixin, TestCase):
    """ TestCase for testing cron jobs """
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_event_places.json',
        'load_event_types.json',
        'load_events.json'
    ]

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    @allure.story('job')
    @allure.severity(Severity.CRITICAL)
    def test_update_expire_job(self):
        self.event.date_expire = datetime.now() - timedelta(seconds=1)
        self.event.save()
        self.assertEqual(self.event.is_finished, False)

        job = EventsMarkFinishedCronJob()
        job.do()
        event = Event.objects.get(pk=self.event.pk)
        self.assertEqual(event.is_finished, True)
