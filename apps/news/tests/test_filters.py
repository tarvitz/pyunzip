# -*- coding: utf-8 -*-
"""
.. module:: apps.news.tests.test_filters
    :synopsis: Filters unit testing for news app
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""


import allure
from django.test import TestCase
from allure.constants import Severity
from apps.news.templatetags.newsfilters import render_filter, textile_filter


@allure.feature('Filters: Event')
class NewsFiltersTest(TestCase):
    """
    News filters testing
    """

    @allure.story('filter')
    @allure.severity(Severity.CRITICAL)
    def test_news_cut(self):
        """
        news cut filter test
        """
        test_message = "Here the test message"
        expected = '\t<p>%s</p>' % test_message
        self.assertEqual(expected, render_filter(test_message, 'textile'))
        self.assertEqual(expected, render_filter(test_message, 'non existent'))
        self.assertEqual(expected, textile_filter(test_message))
