# coding: utf-8

from apps.files.models import Gallery
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from tastypie.test import ResourceTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
import simplejson as json
from copy import deepcopy


class GalleryViewSetMixin(object):
    model_class = Gallery
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_galleries.json'
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


class GalleryViewSetAnonymousUserTest(TestHelperMixin,
                                      GalleryViewSetMixin,
                                      ApiAnonymousUserTestCaseMixin,
                                      APITestCase):
    pass


class GalleryViewSetAdminUserTest(TestHelperMixin,
                                  GalleryViewSetMixin,
                                  ApiAdminUserTestCaseMixin,
                                  APITestCase):
    pass


class GalleryViewSetUserTest(TestHelperMixin,
                             GalleryViewSetMixin,
                             ApiAdminUserTestCaseMixin,
                             APITestCase):
    pass