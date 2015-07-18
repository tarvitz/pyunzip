# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.accounts.models import PM

from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
import allure
from allure.constants import Severity

import simplejson as json


__all__ = [
    'PMViewSetAdminUserTest', 'PMViewSetAnonymousUserTest',
    'PMViewSetTestMixin', 'PMViewSetUserNotOwnerTest', 'PMViewSetUserTest'
]


class PMViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_pms.json',
    ]

    def setUp(self):
        self.maxDiff = None
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.pm = PM.objects.get(pk=1)

        self.url_detail = reverse(
            'api:pm-detail', args=(self.pm.pk, ))

        self.url_list = reverse('api:pm-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.pm.pk,
            'addressee': reverse('api:user-detail',
                                 args=(self.other_user.pk, )),
            'cache_content': '\t<p>dasdad</p>',
            'content': 'dasdad',
            'dba': False,
            'dbs': False,
            'is_read': False,
            'sender': reverse('api:user-detail', args=(self.user.pk, )),
            'syntax': 'textile',
            'title': u'title and so on'
        }
        self.patch = {
            'title': u'New pm comment and so on',
        }
        self.post = {
            'addressee': reverse('api:user-detail',
                                 args=(self.other_user.pk, )),
            'content': u'here is a ne pm **bold**',
            'dba': False,
            'dbs': False,
            'is_read': False,
            # optional field
            'sender': reverse('api:user-detail', args=(self.user.pk, )),
            'syntax': settings.DEFAULT_SYNTAX,
            'title': u'New message',
        }
        self.object_detail_response = {
            'addressee': 'http://testserver/api/users/2/',
            'cache_content': '\t<p>Вот еба!</p>',
            'content': 'Вот еба!',
            'dba': False,
            'dbs': False,
            'is_read': True,
            'sender': 'http://testserver/api/users/1/',
            'sent': '2014-05-27T03:41:09.889000',
            'syntax': None,
            'title': 'сообщение',
            'url': 'http://testserver/api/pms/1/'
        }


@allure.feature('API: Private Messages')
class PMViewSetAnonymousUserTest(PMViewSetTestMixin, TestHelperMixin,
                                 APITestCase):
    def setUp(self):
        super(PMViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(
            load,
            {'detail': _('Authentication credentials were not provided.')})

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load,
            {'detail': _('Authentication credentials were not provided.')})

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))


@allure.feature('API: Private Messages')
class PMViewSetAdminUserTest(PMViewSetTestMixin, TestHelperMixin,
                             APITestCase):
    # test admin user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_admin_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_admin_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), PM.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_admin_put_detail(self):
        self.login('admin')
        count = PM.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(PM.objects.count(), count)

        put = dict(**self.put)
        #: todo make checks automatically
        load.pop('url')
        load.pop('sent')
        self.check_response(put, load)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_admin_post_list(self):
        """
        accounts.change_pm permission holder users can freely assign
        sender to anyone, other users can only create pms for themselves

        :return:
        """
        self.login('admin')
        count = PM.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_admin_patch_detail(self):
        self.login('admin')
        count = PM.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = PM.objects.get(pk=self.pm.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(PM.objects.count(), count)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_admin_delete_detail(self):
        self.login('admin')
        count = PM.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PM.objects.count(), count - 1)


@allure.feature('API: Private Messages')
class PMViewSetUserTest(PMViewSetTestMixin, TestHelperMixin,
                        APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(PMViewSetUserTest, self).setUp()

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(self.object_detail_response, load)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        qset = Q(sender=self.user) | Q(addressee=self.user)
        self.assertEqual(len(load['results']), PM.objects.filter(qset).count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load,
            {'detail': _('You do not have permission to perform this action.')}
        )

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        self.login('user')
        count = PM.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_optional(self):
        self.login('user')
        post = dict(**self.post)
        post.pop('sender')
        count = PM.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)
        pm = PM.objects.latest('pk')
        self.assertEqual(pm.sender, self.user)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_no_owner(self):
        self.login('user')
        post = dict(**self.post)
        post.update({
            'sender': reverse('api:user-detail', args=(self.admin.pk, ))
        })
        count = PM.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)
        pm = PM.objects.latest('pk')
        # user can not send messages from the 'other' users
        self.assertEqual(pm.sender, self.user)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load,
            {'detail': _('You do not have permission to perform this action.')}
        )

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login('user')
        count = PM.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(PM.objects.count(), count)
        self.assertEqual(
            load,
            {'detail': _('You do not have permission to perform this action.')}
        )


@allure.feature('API: Private Messages')
class PMViewSetUserNotOwnerTest(PMViewSetTestMixin, TestHelperMixin,
                                APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(PMViewSetUserNotOwnerTest, self).setUp()

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        """Anyone except sender, addressee would retrieve 404"""

        self.pm.addressee = self.admin
        self.pm.save()

        self.login('user2')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(force_text(_('Not found.')), load['detail'])

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('user2')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        qset = Q(addressee=self.other_user) | Q(sender=self.other_user)
        self.assertEqual(len(load['results']), PM.objects.filter(qset).count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        self.login('user2')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        """
        any user can create his own pm, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        post = dict(**self.post)
        addressee, sender = post['sender'], post['addressee']
        post.update({
            'addressee': addressee,
            'sender': sender
        })

        count = PM.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_to_self(self):
        """
        check for non-possibility to send pm for self

        :return:
        """
        self.login('user2')
        post = dict(**self.post)

        count = PM.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(PM.objects.count(), count)
        self.assertEqual(load['addressee'][0],
                         force_text(_("You can not send pm for yourself")))

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_no_owner_set(self):
        """
        post without owner, as it default would be assign to current user
        :return:
        """
        self.login('user2')
        count = PM.objects.count()
        post = dict(**self.post)
        post.pop('sender')
        post.update({
            'addressee': reverse('api:user-detail', args=(self.user.pk, ))
        })
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(PM.objects.count(), count + 1)
        self.check_response(load, post)
        pm = PM.objects.latest('id')
        self.assertEqual(pm.sender, self.other_user)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        self.login('user2')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login('user2')
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))
