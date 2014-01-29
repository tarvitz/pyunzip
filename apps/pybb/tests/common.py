# coding: utf-8
from django.test import TestCase
from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = []

    def setUp(self):
        self.urls_void = [
        ]
        self.urls_registered = [
        ]
        self.get_object = get_object_or_None

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