# coding: utf-8
from django.contrib.auth import get_user_model
from apps.files.models import Image
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin,
    ApiUserOwnerTestCaseMixin
)
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from unittest import TestCase
from app.settings import rel

User = get_user_model()


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
        self.user = User.objects.get(username='user')

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
            'owner': 'http://testserver/api/users/6/',
            'url': 'http://testserver/api/images/1/'
        }


class ImageViewSetAnonymousUserTest(ImageViewSetMixin,
                                    ApiAnonymousUserTestCaseMixin,
                                    APITestCase):
    pass


class ImageViewSetAdminUserTest(ImageViewSetMixin,
                                ApiAdminUserTestCaseMixin,
                                APITestCase):
    pass


class ImageViewSetUserTest(ImageViewSetMixin,
                           ApiUserOwnerTestCaseMixin,
                           APITestCase):
    pass