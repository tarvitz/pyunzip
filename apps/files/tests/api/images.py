# coding: utf-8

from apps.files.models import Image
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from unittest import TestCase
from app.settings import rel


class ImageViewSetMixin(TestCase):
    model_class = Image
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_galleries.json',
        'tests/fixtures/load_images.json',
    ]

    def setUp(self):
        super(ImageViewSetMixin, self).setUp()
        self.post_format = 'multipart'

        self.patch = {
            'title': 'new image',
            'comments': u'Comments are here'
        }
        self.put = {
            'title': 'title',
            'alias': 'ti',
            'comments': 'comment',
            'gallery': reverse('api:gallery-detail', args=(1, )),
            'image': open(rel('tests/fixtures/image.jpg'), 'rb'),
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
        }
        self.post = {
            'title': 'title',
            'alias': 'ti',
            'comments': 'comment',
            'gallery': reverse('api:gallery-detail', args=(1, )),
            'image': open(rel('tests/fixtures/image.jpg'), 'rb'),
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
        }
        self.object_detail_response = {
            'title': '2',
            'alias': '',
            'comments': '1',
            'gallery': 'http://testserver/api/galleries/1/',
            'image': 'images/galleries/1/bl.png',
            'owner': 'http://testserver/api/users/1/',
            'url': 'http://testserver/api/images/1/'
        }


class ImageViewSetAnonymousUserTest(TestHelperMixin, ImageViewSetMixin,
                                    ApiAnonymousUserTestCaseMixin,
                                    APITestCase):
    pass


class ImageViewSetAdminUserTest(TestHelperMixin, ImageViewSetMixin,
                                ApiAdminUserTestCaseMixin,
                                APITestCase):
    pass


class ImageViewSetUserTest(TestHelperMixin,
                           ImageViewSetMixin,
                           ApiAdminUserTestCaseMixin,
                           APITestCase):
    pass