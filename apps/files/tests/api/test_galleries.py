# coding: utf-8

from apps.files.models import Gallery
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from rest_framework.test import APITestCase
from unittest import TestCase


class GalleryViewSetMixin(TestCase):
    model_class = Gallery
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_galleries.json'
    ]

    def setUp(self):
        super(GalleryViewSetMixin, self).setUp()
        self.patch = {
            'name': 'tezt'
        }
        self.put = {
            'name': 'tetest',
            'type': 'user'
        }
        self.post = {
            'name': 'testme',
            'type': 'tech',
        }
        self.object_detail_response = {
            'name': 'test', 'type': 'global',
            'url': 'http://testserver/api/galleries/1/'
        }


class GalleryViewSetAnonymousUserTest(GalleryViewSetMixin,
                                      ApiAnonymousUserTestCaseMixin,
                                      APITestCase):
    pass


class GalleryViewSetAdminUserTest(GalleryViewSetMixin,
                                  ApiAdminUserTestCaseMixin,
                                  APITestCase):
    pass


class GalleryViewSetUserTest(GalleryViewSetMixin,
                             ApiAdminUserTestCaseMixin,
                             APITestCase):
    pass