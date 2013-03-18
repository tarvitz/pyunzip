# coding: utf-8
#from django.utils import unittest
from django.test import TestCase
from django.test.client import RequestFactory, Client
#from django.core.urlresolvers import reverse

class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
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

        urls_params = []
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
        #import ipdb
        #ipdb.set_trace()
        pass

    def test_urls_user(self):
        loggined = self.client.login(username='user', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()

    def test_urls_admin(self):
        loggined = self.client.login(username='admin', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()