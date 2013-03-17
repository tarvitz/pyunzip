# coding: utf-8
from django.utils import unittest
from django.test.client import RequestFactory
from apps.core.helpers import (
    post_markup_filter,
) 

class CodeTest(unittest.TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    """ testing helpers module """
    def test_post_markup_unicode(self):
        quote_source = u"(Пользователь){цитата}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

    def test_post_markup(self):
        quote_source = u"(User){quote}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

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
                print msg
            raise AssertionError