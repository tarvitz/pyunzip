# coding: utf-8

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.urlresolvers import reverse


from apps.karma.models import Karma
from apps.core.tests import TestHelperMixin


class KarmaTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.post = {
            'comment': u'+1'
        }

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

    def test_karma_alter_timeout(self):
        Karma.objects.create(user=self.admin, voter=self.user, value=1,
                             comment=u'New')
        self.login('user')
        url = reverse('karma:karma-alter', args=('down', self.user.nickname, ))
        count = Karma.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Karma.objects.count(), count)
        self.assertEqual(response.context['request'].get_full_path(),
                         reverse('core:timeout'))

    def test_self_karma_alter(self):
        """
        self karma alterations are forbidden

        :return:
        """
        self.login(self.user.username)
        url = reverse('karma:karma-alter', args=('up', self.user.nickname, ))
        count = Karma.objects.count()
        karma_amount = self.user.karma
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Karma.objects.count(), count)