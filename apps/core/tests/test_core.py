# coding: utf-8

import six

if six.PY3:
    file = None

from django.test import TestCase
from apps.core.helpers import (
    post_markup_filter,
)
from apps.core.connections import get_redis_client
from django.core.urlresolvers import reverse

import allure
from allure.constants import Severity

import logging
logger = logging.getLogger(__name__)


@allure.feature('General: Core')
class CoreTest(TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_news_categories.json',
        'load_news.json',
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    """ helpers """
    def process_messages(self, instance, kw, fx=None):
        fx = fx or {}
        messages = []
        for (key, value) in kw.items():
            try:
                if key in fx:
                    self.assertEqual(getattr(instance, key),
                                     fx[key].objects.get(pk=value))
                else:
                    self.assertEqual(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key,
                    'value': value
                })
        return messages

    @allure.story('urls')
    @allure.severity(Severity.NORMAL)
    def test_urls(self):
        prefix = 'core'
        urls = [
            'permission-denied',
            'currently-unavailable',
            'wot_verification',
            # static
            'vote-invalid-object',
            'karma-self-alter',
            'karma-power-insufficient',
            'user-not-exists',
            'timeout',
            'rules',
            'faq',
            'pm-success',
            'sender-limit-error',
            'addressee-limit-error',
            'pm-permission-denied',
            'pm-deleted',
            'permission-denied',
            'image-undeletable',
            'image-deleted',
            'password-changed'

        ]
        messages = []
        for user in ['user', 'admin', None]:
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            for url in urls:
                _url = reverse('%s:%s' % (prefix, url))
                try:
                    response = self.client.get(_url, follow=True)
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({
                        'err': err,
                        'url': _url,
                        'user': user
                    })
        if messages:
            for msg in messages:
                logger.info(
                    "Could not get url %(user)s in %(url)s, got %(err)s" % msg
                )
            raise AssertionError

    @allure.story('markup')
    @allure.severity(Severity.NORMAL)
    def test_post_markup_unicode(self):
        quote_source = u"(Пользователь){цитата}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

    @allure.story('markup')
    @allure.severity(Severity.NORMAL)
    def test_post_markup(self):
        quote_source = u"(User){quote}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

    @allure.story('markup')
    @allure.severity(Severity.NORMAL)
    def test_post_markup_variations(self):
        quotes = [
            u'(User){quote\n\n\n\nnquote}',
            u'(User){\n\nq\n\n\ote}',
            u'(User){\na\n}'
        ]
        messages = []
        for (index, quote) in enumerate(quotes):
            try:
                self.assertNotIn(post_markup_filter(quote), quotes[index])
            except AssertionError as err:
                messages.append(err)

        if messages:
            for msg in messages:
                logging.warn(msg)
            raise AssertionError

    @allure.story('redis')
    @allure.severity(Severity.NORMAL)
    def test_redis_client_single_instance(self):
        """
        redis client you can get in apps.core.connections is single instance
        """
        with allure.step('setup environment'):
            connection_one = get_redis_client()
            connection_two = get_redis_client()
        with allure.step('check connections'):
            self.assertEqual(id(connection_one), id(connection_two))
