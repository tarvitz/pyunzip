# coding: utf-8

from apps.files.models import Gallery
from apps.core.tests import (
    ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from rest_framework.test import APITestCase
import allure
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


@allure.feature('API: Galleries')
class GalleryViewSetAnonymousUserTest(GalleryViewSetMixin,
                                      ApiAnonymousUserTestCaseMixin,
                                      APITestCase):
    """
    Gallery api test cases for anonymous user (not authenticated)
    """


@allure.feature('API: Galleries')
class GalleryViewSetAdminUserTest(GalleryViewSetMixin,
                                  ApiAdminUserTestCaseMixin,
                                  APITestCase):
    """
    Gallery api test cases for admin user
    """


@allure.feature('API: Galleries')
class GalleryViewSetUserTest(GalleryViewSetMixin,
                             ApiAdminUserTestCaseMixin,
                             APITestCase):
    """
    Gallery api test cases for common user (authenticated)
    """
