# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.tracker.models import SeenObject
from apps.core.helpers import model_json_encoder
from apps.news.models import News
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.conf import settings
import simplejson as json

from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json'
    ]

    def setUp(self):
        self.request_factory = RequestFactory()
        self.urls_void = [
        ]
        self.urls_registered = [
        ]
        self.urls_params = [
        ]
        self.unlink_files = []

    def tearDown(self):
        pass

    def print_form_errors(self, form):
        if 'errors' in form:
            for (key, items) in form['errors'].items():
                print "%(key)s: %(items)s" % {
                    'key': key,
                    'items': ", ".join(items)
                }

    def no_test_urls_params(self):
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

    def test_hmenu(self):
        pass
