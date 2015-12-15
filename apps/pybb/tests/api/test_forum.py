# -*- coding: utf-8 -*-
"""
.. module:: apps.pybb.tests.api.test_forum
    :synopsis: Forum model api test cases
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from apps.accounts.models import User
from apps.core.tests import (
    ApiAdminUserTestCaseMixin, ApiAnonymousUserTestCaseMixin,
)
from apps.pybb.models import Forum
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
import allure


class ForumViewSetMixin(object):
    """
    Category access mixin
    """
    model_class = Forum
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_pybb_categories.json',
        'load_forums.json'
    ]

    def setUp(self):
        super(ForumViewSetMixin, self).setUp()
        self.post_format = 'multipart'
        self.user = User.objects.get(username='user')

        self.patch = {
            'name': 'new name',
            'position': 1,
            'description': 'bla'
        }
        self.put = {
            "url": reverse('api:forum-detail', args=(1, )),
            "name": "Space Marines",
            "position": 0,
            "description": "",
            # "updated": "2015-07-08T23:01:53.302133",
            "post_count": 1,
            "css_icon": "icon-github",
            "is_hidden": False,
            "is_private": False,
            "category": reverse('api:category-detail', args=(1, )),
            "moderators": [
                reverse('api:user-detail', args=(1, )),
            ],
            "participants": [
                reverse('api:user-detail', args=(1, ))
            ]
        }
        self.post = {
            "name": "Space Marines",
            "position": 0,
            "description": "",
            "updated": "2015-07-08T23:01:53.302133",
            "post_count": 1,
            "css_icon": "icon-github",
            "is_hidden": False,
            "is_private": False,
            "category": reverse('api:category-detail', args=(1, )),
            "moderators": [
                reverse('api:user-detail', args=(1, )),
            ],
            "participants": [
                reverse('api:user-detail', args=(1, ))
            ]
        }
        self.object_detail_response = {
            "url": "http://testserver/api/forums/1/",
            "name": "Tech support",
            "position": 0,
            "description": "",
            "updated": "2013-12-26T16:55:07.069000",
            "post_count": 1,
            "css_icon": "",
            "is_hidden": False,
            "is_private": False,
            "category": "http://testserver/api/categories/1/",
            "moderators": [
                "http://testserver/api/users/1/"
            ],
            "participants": []
        }


@allure.feature('API: Category')
class ForumViewSetAnonymousUserTest(ForumViewSetMixin,
                                    ApiAnonymousUserTestCaseMixin,
                                    APITestCase):
    pass


@allure.feature('API: Category')
class ForumViewSetAdminUserTest(ForumViewSetMixin,
                                ApiAdminUserTestCaseMixin,
                                APITestCase):
    pass


@allure.feature('API: Category')
class ForumViewSetUserTest(ForumViewSetMixin,
                           ApiAnonymousUserTestCaseMixin,
                           APITestCase):
    pass
