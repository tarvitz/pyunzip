# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()
from apps.wh.models import Army, Side
from apps.tabletop.models import Report, Codex
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse

from apps.core.helpers import get_content_type

import simplejson as json
from copy import deepcopy


class ReportViewSetTestMixin(object):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_sides.json',
        'tests/fixtures/load_armies.json',
        'tests/fixtures/load_codexes.json',
        'tests/fixtures/load_rosters.json',
        'tests/fixtures/load_games.json',
        'tests/fixtures/load_missions.json',
        'tests/fixtures/load_reports.json',
    ]

    def setUp(self):
        self.maxDiff = None
        self.side_ct = get_content_type(Side)
        self.army_ct = get_content_type(Army)
        # update content types
        Codex.objects.filter(content_type_id=17).update(
            content_type=self.side_ct)

        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.report = Report.objects.get(pk=1)
        self.codex = Codex.objects.get(pk=1)
        self.url_detail = reverse(
            'api:report-detail', args=(self.report.pk, ))

        self.url_list = reverse('api:report-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
        }
        self.patch = {
            'comment': u'New comment **here**',
            'is_draw': True,
        }
        self.post = {

        }
        self.object_detail_response = {
            'comment': u'\u0422\u0443\u0442 \u043e\u0447\u0435\u043d\u044c '
                       u'\u0431\u043e\u043b\u044c\u0448\u043e\u0439 \u0431'
                       u'\u0430\u0442\u043b \u0440\u0435\u043f\u043e\u0440'
                       u'\u0442.',
            'comment_cache': u'\t<p>\u0422\u0443\u0442 \u043e\u0447\u0435'
                             u'\u043d\u044c \u0431\u043e\u043b\u044c'
                             u'\u0448\u043e\u0439 \u0431\u0430\u0442\u043b '
                             u'\u0440\u0435\u043f\u043e\u0440\u0442.</p>',
            'created_on': '2014-06-17T04:59:03.339',
            'deployment': 'dow',
            'is_approved': False,
            'is_draw': False,
            'layout': '1vs1',
            'mission': 'http://testserver/api/missions/6/',
            'owner': 'http://testserver/api/users/1/',
            'rosters': [],
            'syntax': '',
            'title': u'\u0411\u0438\u0442\u0432\u0430 \u0437\u0430 '
                     u'\u0431`\u0430\u0442\u0432\u0443',
            'url': 'http://testserver/api/reports/1/',
            'winners': []
        }


class ReportViewSetAnonymousUserTest(ReportViewSetTestMixin, TestHelperMixin,
                                     APITestCase):
    def setUp(self):
        super(ReportViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')


class ReportViewSetAdminUserTest(ReportViewSetTestMixin, TestHelperMixin,
                                 APITestCase):
    # test admin user
    def test_admin_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_admin_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    def test_admin_put_detail(self):
        self.login('admin')
        count = Report.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(Report.objects.count(), count)

    def test_admin_post_list(self):
        """
        tabletop.change_report permission holder users can freely assign
        owner to anyone, other users can only create reports for themselves

        :return:
        """
        self.login('admin')
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    def test_admin_patch_detail(self):
        self.login('admin')
        count = Report.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Report.objects.get(pk=self.report.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Report.objects.count(), count)

    def test_admin_delete_detail(self):
        self.login('admin')
        count = Report.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), count - 1)


class ReportViewSetUserTest(ReportViewSetTestMixin, TestHelperMixin,
                            APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(ReportViewSetUserTest, self).setUp()

    def test_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

    def test_post_list(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_no_owner(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Report.objects.get(pk=self.report.pk)
        self.check_instance(obj, load, self.patch)

    def test_delete_detail(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Report.objects.count(), count - 1)


class ReportViewSetUserNotOwnerTest(ReportViewSetTestMixin, TestHelperMixin,
                                    APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(ReportViewSetUserNotOwnerTest, self).setUp()

    def test_get_detail(self):
        self.login('user2')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('user2')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    def test_put_detail(self):
        self.login('user2')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_post_list(self):
        """
        any user can create his own report, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        post = deepcopy(self.post)
        post.update({
            'owner': reverse('api:user-detail', args=(self.other_user.pk, ))
        })
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_no_owner_set(self):
        """
        post without owner, as it default would be assign to current user
        :return:
        """
        self.login('user2')
        count = Report.objects.count()
        post = deepcopy(self.post)
        post.pop('owner')
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)
        report = Report.objects.latest('id')
        self.assertEqual(report.owner, self.other_user)

    def test_patch_detail(self):
        self.login('user2')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_delete_detail(self):
        self.login('user2')
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')