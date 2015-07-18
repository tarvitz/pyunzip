# coding: utf-8

from apps.accounts.models import User
from apps.wh.models import Army, Side
from apps.tabletop.models import Report, Codex, Roster
from apps.tabletop.serializers import FAILURE_MESSAGES
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.conf import settings

from apps.core.helpers import get_content_type

import simplejson as json
import allure
from allure.constants import Severity


class ReportViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_sides.json',
        'load_armies.json',
        'load_codexes.json',
        'load_rosters.json',
        'load_games.json',
        'load_missions.json',
        'load_reports.json',
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
            'id': 1,
            'comment': u'new comment put',
            'is_draw': False,
            'mission': reverse('api:mission-detail', args=(3, )),
            'layout': '1vs1',
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
            'rosters': [
                reverse('api:roster-detail', args=(1, )),
                reverse('api:roster-detail', args=(3, ))
            ],
            'winners': [
                reverse('api:roster-detail', args=(3, ))
            ],
            'title': u'New report',
            'syntax': settings.DEFAULT_SYNTAX
        }
        self.patch = {
            'comment': u'New comment **here**',
            'is_draw': True,
        }
        self.post = {
            'comment': u'new comment',
            'is_draw': False,
            'mission': reverse('api:mission-detail', args=(1, )),
            'layout': '1vs1',
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
            'rosters': [
                reverse('api:roster-detail', args=(1, )),
                reverse('api:roster-detail', args=(2, ))
            ],
            'winners': [
                reverse('api:roster-detail', args=(1, ))
            ],
            'title': u'New report',
            'syntax': settings.DEFAULT_SYNTAX
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
            'created_on': '2014-06-17T04:59:03.339000',
            'deployment': 'dow',
            'is_approved': False,
            'is_draw': False,
            'layout': '1vs1',
            'mission': 'http://testserver/api/missions/6/',
            'owner': 'http://testserver/api/users/2/',
            'rosters': [],
            'syntax': '',
            'title': u'\u0411\u0438\u0442\u0432\u0430 \u0437\u0430 '
                     u'\u0431`\u0430\u0442\u0432\u0443',
            'url': 'http://testserver/api/reports/1/',
            'winners': []
        }


@allure.feature('API: Reports')
class ReportViewSetAnonymousUserTest(ReportViewSetTestMixin, TestHelperMixin,
                                     APITestCase):
    def setUp(self):
        super(ReportViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

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


@allure.feature('API: Reports')
class ReportViewSetAdminUserTest(ReportViewSetTestMixin, TestHelperMixin,
                                 APITestCase):
    # test admin user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        self.login('admin')
        count = Report.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = dict(**self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(Report.objects.count(), count)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
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

        post = dict(**self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
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

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login('admin')
        count = Report.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), count - 1)


@allure.feature('API: Reports')
class ReportViewSetUserTest(ReportViewSetTestMixin, TestHelperMixin,
                            APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(ReportViewSetUserTest, self).setUp()

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        put = dict(**self.put)
        put.pop('id')
        self.check_response(load, put)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_failure(self):
        self.login('user')
        post = dict(**self.post)
        winners = Roster.objects.filter(pk__in=[3, 4])

        post['winners'] = [
            reverse('api:roster-detail', args=(3, )),
            reverse('api:roster-detail', args=(4, )),
        ]

        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['non_field_errors']), 2)
        for idx, winner in enumerate(winners):
            self.assertEqual(
                load['non_field_errors'][idx],
                force_text(FAILURE_MESSAGES['wrong_winner_rosters'] % winner)
            )

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_no_owner(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(Report.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Report.objects.get(pk=self.report.pk)
        self.check_instance(obj, load, self.patch)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Report.objects.count(), count - 1)


@allure.feature('API: Reports')
class ReportViewSetUserNotOwnerTest(ReportViewSetTestMixin, TestHelperMixin,
                                    APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(ReportViewSetUserNotOwnerTest, self).setUp()

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('user2')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('user2')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Report.objects.count())

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
        any user can create his own report, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        post = dict(**self.post)
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

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_no_owner_set(self):
        """
        post without owner, as it default would be assign to current user

        :return:
        """
        self.login('user2')
        count = Report.objects.count()
        post = dict(**self.post)
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

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list_false_owner_set(self):
        """
        post without owner, as it default would be assign to current user

        :return:
        """
        self.login('user2')
        count = Report.objects.count()
        post = dict(**self.post)
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(Report.objects.count(), count)
        self.assertEqual(load['owner'][0],
                         force_text(FAILURE_MESSAGES['wrong_owner']))

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
