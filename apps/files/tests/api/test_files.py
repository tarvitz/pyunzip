# coding: utf-8
from django.contrib.auth import get_user_model
from apps.files.models import UserFile
from apps.core.tests import (
    ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin,
    ApiUserOwnerTestCaseMixin, ApiUserNotOwnerTestCaseMixin
)
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from unittest import TestCase
from app.settings import rel

User = get_user_model()


class UserFileViewSetMixin(TestCase):
    model_class = UserFile
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_user_files.json',
    ]

    def setUp(self):
        super(UserFileViewSetMixin, self).setUp()
        self.post_format = 'multipart'
        self.user = User.objects.get(username='user')

        self.patch = {
            'title': 'new user_file',
        }
        self.put = {
            'title': 'new title',
            'file': open(rel('tests/fixtures/user_file.zip'), 'rb'),
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
        }
        self.post = {
            'title': 'title',
            'file': open(rel('tests/fixtures/user_file.zip'), 'rb'),
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
        }
        self.object_detail_response = {
            'file': 'http://testserver/uploads/user/1/files/1.png',
            'owner': 'http://testserver/api/users/2/',
            'plain_type': 'image/png',
            'size': 429202,
            'title': '',
            'url': 'http://testserver/api/userfiles/1/'
        }


class UserFileViewSetAnonymousUserTest(UserFileViewSetMixin,
                                       ApiAnonymousUserTestCaseMixin,
                                       APITestCase):
    pass


class UserFileViewSetAdminUserTest(UserFileViewSetMixin,
                                   ApiAdminUserTestCaseMixin,
                                   APITestCase):
    pass


class UserFileViewSetUserNotOwnerTest(UserFileViewSetMixin,
                                      ApiUserNotOwnerTestCaseMixin,
                                      APITestCase):
    pass


class UserFileViewSetUserTest(UserFileViewSetMixin,
                              ApiUserOwnerTestCaseMixin,
                              APITestCase):
    pass
