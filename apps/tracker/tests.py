# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.tracker.models import SeenObject
from apps.core.helpers import model_json_encoder
from apps.news.models import News
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
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

    def test_tracher_json_mark_read(self):
        # test for user
        n = News.objects.all()[0]
        user = User.objects.get(username='user')
        app_n_model = '%s.%s' % (
            n._meta.app_label,
            n._meta.module_name
        )
        ct = ContentType.objects.get(
            app_label=n._meta.app_label, model=n._meta.module_name
        )
        soes = SeenObject.objects.filter(content_type=ct, object_pk=str(n.pk))
        users = [i.user for i in soes]
        self.assertNotIn(user, users)
        url = reverse('json:tracker:mark-read', args=(app_n_model, n.pk))
        # test for anonymous
        # anonymous is forbidden to use it
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        js = json.loads(response.content)
        self.assertEqual(js['error'].lower(), 'login required')

        # test for user
        logged = self.client.login(username='user', password='123456')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        soes = SeenObject.objects.filter(content_type=ct, object_pk=str(n.pk))
        users = [i.user for i in soes]
        self.assertIn(user, users)