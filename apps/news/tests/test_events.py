# coding: utf-8

from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse

from apps.core.tests import TestHelperMixin
from apps.news.models import (
    Event, EVENT_TYPE_CHOICES
)

import allure
from allure.constants import Severity


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
