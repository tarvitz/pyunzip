# coding: utf-8
import logging
from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
import allure
from allure.constants import Severity


logger = logging.getLogger(__file__)


@allure.feature('Benchmark: News')
class BenchmarkTest(TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_news_categories.json',
    ]

    def setUp(self):
        from apps.news import views
        self.views = views
        logger.info("Run benchmarking tests for news")

    def tearDown(self):
        logger.info("End of benchmarking tests for news")

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_news(self):
        for user in ['user', 'admin', None]:
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            results = []
            url = reverse('news:news')
            for i in range(1, 10):
                n = datetime.now()
                self.client.get(url)
                offset = datetime.now() - n
                results.append(offset.total_seconds())
            minimum = min(results)
            maximum = max(results)
            avg = sum(results) / len(results)
            msg = {
                'url': url, 'user': user or 'Anonymous',
                'min': minimum, 'max': maximum, 'avg': avg
            }
            logger.info(
                "Benchmarking %(user)s %(url)s: min: %(min)s, "
                "max: %(max)s, avg: %(avg)s" % msg
            )
