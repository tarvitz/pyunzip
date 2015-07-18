# coding: utf-8

from django.test import TestCase
from apps.accounts.models import User

from django.core.urlresolvers import reverse
from django.conf import settings

from apps.karma.models import Karma
from apps.core.tests import TestHelperMixin
import allure
from allure.constants import Severity


@allure.feature('General: Karma')
class KarmaTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.post = {
            'comment': u'+1'
        }

    @allure.story('alter')
    @allure.severity(Severity.NORMAL)
    def test_karma_up(self):
        self.login('admin')
        url = reverse('karma:karma-alter', args=('up', self.user.nickname, ))
        count = Karma.objects.count()
        karma_amount = self.user.karma
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Karma.objects.count(), count + 1)
        karma = Karma.objects.latest('pk')
        self.assertEqual(karma.value, 1)
        self.assertEqual(karma.user.karma, karma_amount + karma.value)
        self.assertEqual(karma.comment, self.post['comment'])

    @allure.story('alter')
    @allure.severity(Severity.NORMAL)
    def test_karma_down(self):
        self.login('admin')
        url = reverse('karma:karma-alter', args=('down', self.user.nickname, ))
        count = Karma.objects.count()
        karma_amount = self.user.karma
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Karma.objects.count(), count + 1)
        karma = Karma.objects.latest('pk')
        self.assertEqual(karma.value, -1)
        self.assertEqual(karma.user.karma, karma_amount + karma.value)
        self.assertEqual(karma.comment, self.post['comment'])

    @allure.story('access')
    @allure.severity(Severity.NORMAL)
    def test_karma_alter_timeout(self):
        for item in range(settings.KARMA_PER_TIMEOUT_AMOUNT + 1):
            Karma.objects.create(
                user=self.admin, voter=self.user, value=1,
                comment=u'New karma modification' + str(item)
            )
        self.login('user')
        url = reverse('karma:karma-alter', args=('down', self.user.nickname, ))
        count = Karma.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Karma.objects.count(), count)
        self.assertEqual(response.context['request'].get_full_path(),
                         reverse('core:timeout'))

    @allure.story('alter')
    @allure.severity(Severity.NORMAL)
    def test_self_karma_alter(self):
        """
        self karma alterations are forbidden

        :return:
        """
        self.login(self.user.username)
        url = reverse('karma:karma-alter', args=('up', self.user.nickname, ))
        count = Karma.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Karma.objects.count(), count)
