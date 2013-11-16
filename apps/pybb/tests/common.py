# coding: utf-8
#from django.utils import unittest
from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from apps.core.helpers import get_object_or_None
from apps.core.tests import TestHelperMixin


class JustTest(TestCase):
    fixtures = [
    ]

    def setUp(self):
        self.urls_void = [
        ]
        self.urls_registered = [
        ]
        self.get_object = get_object_or_None

    def test_registered_urls(self):
        messages = []
        for user in ('admin', 'user'):
            logged = self.client.login(username=user, password='123456')
            self.assertEqual(logged, True)
            for url in self.urls_registered:
                response = self.client.get(url, follow=True)
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({
                        'user': user, 'err': err, 'url': url
                    })
        if messages:
            for msg in messages:
                print "Got assertion on %(url)s with %(user)s: %(err)s" % msg
            raise AssertionError

    def tearDown(self):
        pass

    def check_state(self, instance, data, check=lambda x: x):
        messages = []
        for (key, value) in data.items():
            try:
                check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print "Got %(err)s in %(key)s" % msg
            raise AssertionError


class CacheTest(TestCase):
    #fixtures = [
    #]

    def setUp(self):
        pass

    def tearDown(self):
        pass


class BenchmarkTest(TestHelperMixin, TestCase):
    index_url = reverse('pybb_index')

    def setUp(self):
        pass

    def test_index_render(self):
        now = datetime.now()
        response = self.client.get(self.index_url, follow=True)
        process = datetime.now() - now
        print "Got: %s" % process
