# -*- coding: utf-8 -*-
"""
.. module:: apps.pybb.tests.api.test_category
    :synopsis: Category model api test cases
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from apps.accounts.models import User
from apps.core.tests import (
    ApiAdminUserTestCaseMixin, ApiAnonymousUserTestCaseMixin,
)
from apps.pybb.models import Category
from rest_framework.test import APITestCase
import allure


class CategoryViewSetMixin(object):
    """
    Category access mixin
    """
    model_class = Category
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_pybb_categories.json'
    ]

    def setUp(self):
        super(CategoryViewSetMixin, self).setUp()
        self.post_format = 'multipart'
        self.user = User.objects.get(username='user')

        self.patch = {
            'name': 'new name',
            'position': 1
        }
        self.put = {
            'name': 'title',
            'position': 0
        }
        self.post = {
            'name': 'title',
            'position': 1
        }
        self.object_detail_response = {
            'name': 'General',
            'position': 0,
            'url': 'http://testserver/api/categories/1/'
        }


@allure.feature('API: Category')
class CategoryViewSetAnonymousUserTest(CategoryViewSetMixin,
                                       ApiAnonymousUserTestCaseMixin,
                                       APITestCase):
    pass


@allure.feature('API: Category')
class CategoryViewSetAdminUserTest(CategoryViewSetMixin,
                                   ApiAdminUserTestCaseMixin,
                                   APITestCase):
    pass


@allure.feature('API: Category')
class CategoryViewSetUserTest(CategoryViewSetMixin,
                              ApiAnonymousUserTestCaseMixin,
                              APITestCase):
    pass
