# coding: utf-8
from unittest import skipIf
from django.test import TestCase
from django.test.client import RequestFactory
from django.conf import settings
from django.core.cache import cache

import allure
from allure.constants import Severity


@skipIf('apps.menu' not in settings.INSTALLED_APPS, "Disabled")
@allure.feature('General: Menus')
class MenuTest(TestCase):
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
                print(msg)
            raise AssertionError


@skipIf('apps.menu' not in settings.INSTALLED_APPS, "Disabled")
@allure.feature('Cache: Menus')
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

    @allure.story('base')
    @allure.severity(Severity.NORMAL)
    def test_cache_key_prefix(self):
        self.assertEqual(settings.CACHES['default']['KEY_PREFIX'], 'tests')
