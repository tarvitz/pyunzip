# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.menu.models import HMenuItem, VMenuItem
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import model_json_encoder
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.cache import cache
from copy import deepcopy
import simplejson as json

from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_menus.json',
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

    def check_changes(self, instance, keywords, check, check_in=None):
        messages = []
        check_in = check_in or self.assertIn
        for (key, value) in keywords.items():
            try:
                if isinstance(value, list):
                    for item in value:
                        check_in(item, getattr(instance, key).all())
                else:
                    check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                msg = "Got %(err)s in %(key)s" % msg
                print msg
            raise AssertionError


class CacheTest(TestCase):
    fixtures = [
        'tests/fixtures/load_menus.json',
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_hmenu_all(self, report):
        return cache.get('hmenu:all')

    def test_cache_key_prefix(self):
        self.assertEqual(settings.CACHES['default']['KEY_PREFIX'], 'tests')

    def test_hmenu_cache_all(self):
        self.assertEqual(cache.get('hmenu:all'), None)
        self.client.get('/')
        self.assertListEqual(
            list(cache.get('hmenu:all') or []),
            list(HMenuItem.objects.all())
        )