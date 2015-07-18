# coding: utf-8
from apps.accounts.models import User
from apps.files.models import Image
from apps.core.tests import (
    ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin,
    ApiUserOwnerTestCaseMixin, ApiUserNotOwnerTestCaseMixin
)
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from unittest import TestCase
from app.settings import rel
import allure


class ImageViewSetMixin(TestCase):
    model_class = Image
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_galleries.json',
        'load_images.json',
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
            'image': 'http://testserver/uploads/images/galleries/1/bl.png',
            'owner': 'http://testserver/api/users/2/',
            'url': 'http://testserver/api/images/1/'
        }


@allure.feature('API: Images')
class ImageViewSetAnonymousUserTest(ImageViewSetMixin,
                                    ApiAnonymousUserTestCaseMixin,
                                    APITestCase):
    """
    Image api test cases for non authenticated user
    """


@allure.feature('API: Images')
class ImageViewSetAdminUserTest(ImageViewSetMixin,
                                ApiAdminUserTestCaseMixin,
                                APITestCase):
    """
    Image api test cases for admin user (superuser or just privileged one)
    """


@allure.feature('API: Images')
class ImageViewSetUserTest(ImageViewSetMixin,
                           ApiUserOwnerTestCaseMixin,
                           APITestCase):
    """
    Image api test cases for common authenticated user
    """


@allure.feature('API: Images')
class ImageViewSetUserNotOwnerTest(ImageViewSetMixin,
                                   ApiUserNotOwnerTestCaseMixin,
                                   APITestCase):
    """
    Image api test cases for common user who is not an owner of given image
    """
