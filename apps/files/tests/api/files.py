# coding: utf-8
from django.contrib.auth import get_user_model
from apps.files.models import UserFile
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin,
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
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_user_files.json',
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
            'file': 'user/1/files/1.png',
            'owner': 'http://testserver/api/users/6/',
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


class UserFileViewSetUserTest(UserFileViewSetMixin,
                              ApiUserOwnerTestCaseMixin,
                              APITestCase):
    pass


class UserFileViewSetUserNotOwnerTest(UserFileViewSetMixin,
                                      ApiUserNotOwnerTestCaseMixin,
                                      APITestCase):
    pass