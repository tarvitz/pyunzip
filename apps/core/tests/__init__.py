# -*- coding: utf-8 -*-
"""
.. module:: apps.core.tests
    :synopsis: Test cases helpers for unit testing
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import os
import logging
import six
import simplejson as json
import allure
from allure.constants import Severity
from datetime import datetime, date

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q, Model
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from apps.accounts.models import User
from apps.core.tests.test_core import file
if six.PY3:
    import _io


class TestHelperMixin(object):
    def login(self, user, password='123456'):
        if user:
            logged = getattr(self, 'client').login(
                username=user, password=password)
            getattr(self, 'assertEqual')(logged, True)
        else:
            getattr(self, 'client').logout()

    def check_state(self, instance, data, check=lambda x: x, check_in=None):
        messages = []
        check_in = check_in or getattr(self, 'assertIn')
        for (key, value) in data.items():
            try:
                if hasattr(getattr(instance, key), 'all'):
                    for field in getattr(instance, key).all():
                        check_in(field, value)
                else:
                    check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                logging.warning(u"Got %(err)s in %(key)s" % msg)
            raise AssertionError

    @staticmethod
    def proceed_form_errors(context):
        """
        :param context: requires response context instance
            to check form errors and print them to stdout
        :return: None
        """
        if 'form' not in context:
            return

        form = context['form']
        have_errors = (
            getattr(form, 'errors')
            if hasattr(form, 'errors') else False
        )
        if not have_errors:
            return

        logging.warning("Got errors in form:")
        if isinstance(form.errors, dict):
            for key, error_list in form.errors.items():
                logging.warning(
                    "in '%(key)s' got: '%(errors)s'" % {
                        'key': key,
                        'errors': (
                            "; ".join([i for i in error_list])
                            if isinstance(error_list, (list, tuple))
                            else error_list
                        )
                    }
                )
            return
        elif isinstance(form.errors, (list, tuple)):
            for f in form.errors:
                for key, error_list in f.items():
                    logging.warning(
                        u"in '%(key)s got: %(errors)s'" % {
                            'key': key, 'errors': "; ".join([
                                i for i in error_list])
                        }
                    )
        else:
            pass

    def check_instance(self, instance, response, data, assertion=None):
        """ Check instance fields with response keys and data for their
        identification (if assertion is None)

        :param instance: ModelObject ``instance``
        :param dict response: json serialized api response (dict)
        :param dict data: post/put/patch send data
        :keyword assertion: callable assert function for check data
        :return: None
        """
        assertion = assertion or getattr(self, 'assertEqual')
        for field, value in data.items():
            instance_value = getattr(instance, field)
            if isinstance(instance_value, (datetime, )):
                assertion(instance_value.isoformat(), value)
            elif isinstance(instance_value, date):
                assertion(instance_value.isoformat(), value)
            elif isinstance(instance_value, Model):
                assertion(instance_value.get_api_detail_url(), value)
            else:
                assertion(instance_value, value)
                assertion(response[field], value)

    def check_response(self, response, data, assertion=None):
        """Check api response with post data for its identifications
        (if assertion is None)

        :param response: ModelObject ``instance``
        :param dict response: json serialized api response (dict)
        :param dict data: post/put/patch send data
        :keyword assertion: callable assert function for check data
        :return: None
        """
        assertion = assertion or getattr(self, 'assertEqual')
        for field, value in data.items():
            if isinstance(value, (datetime, )):
                assertion(response[field], value.isoformat()[:-3])
            elif isinstance(value, date):
                assertion(response[field], value.isoformat())
            elif isinstance(value, six.string_types):
                if value.startswith('http://testserver'):
                    assertion(response[field],
                              value.replace('http://testserver', ''))
                elif '/api/' in value:
                    assertion(response[field], 'http://testserver' + value)
                else:
                    assertion(response[field], value)
            elif isinstance(value, (tuple, list)) and '/api/' in value[0]:
                for item in value:
                    assertion(
                        'http://testserver' + item in response[field],
                        True
                    )
            elif isinstance(value, (six.PY3 and (_io.TextIOWrapper,
                                                 _io.BufferedReader) or file)):
                # remove uploaded files
                if six.PY3:
                    file_path = os.path.join(
                        settings.MEDIA_ROOT,
                        response[field].replace('http://testserver/uploads/',
                                                '')
                    )
                    self.assertFileExists(file_path)
                    os.unlink(file_path)
                elif six.PY2:
                    self.assertFileExists(response[field])
                    os.unlink(
                        os.path.join(settings.MEDIA_ROOT, response[field])
                    )
                else:
                    raise EnvironmentError("Wrong python version")
            else:
                assertion(response[field], value)

    def assertInstance(self, instance, raw):
        """ assert instance fields with raw post data

        :param instance:
        :param (dict) raw: raw post data for instance creation or its update
        :return:
        """

        verify = dict(**raw)
        m2m_fields = instance._meta.get_m2m_with_model()

        # process m2m relations
        for fields in m2m_fields:
            field = fields[0]
            items = verify.pop(field.name)
            for item in items:
                obj_item = field.rel.to.objects.get(pk=item)
                getattr(self, 'assertIn')(
                    obj_item, getattr(instance, field.name).all())

        for key, value in verify.items():
            getattr(self, 'assertEqual')(getattr(instance, key), value)

    def assertFileExists(self, file_path):
        """ assert file path with MEDIA_ROOT join file existance
        """
        path = os.path.join(settings.MEDIA_ROOT, file_path)
        getattr(self, 'assertEqual')(os.path.exists(path), True)

    def assertResponseStatus(self, response, status):
        try:
            self.assertEqual(status, response.status_code)
            context = response.context
            if context and 'form' in context:
                form = context['form']
                if form.errors:
                    logging.warning(form.errors)
        except AssertionError:
            raise


class ApiTestSourceAssertionMixin(object):
    """
    API test source assertion mixin
    """
    def assertUpdate(self, data, payload, skip_diff=True):
        """
        asserts post/put/patch data given in dict with response one

        :param dict data: user given data to post/put/patch/etc
        :param dict payload: response.data or response payload in json (dict)
        :param bool skip_diff: skip fields that does not include into payload
        :rtype: None
        :return: None
        :raises AssertionError:
            - if one or more fields has not equal data
        """
        errors = []
        for field, item in data.items():
            if field not in payload and skip_diff:
                continue

            value = data[field]
            if isinstance(item, (datetime, )):
                value = data[field].isoformat()[:-3] + '000'
            elif isinstance(item, six.string_types):
                if value.startswith('http://testserver'):
                    value = value.replace('http://testserver', '')
            elif isinstance(item, (list, tuple)):
                _value = []
                for entry in value:
                    if entry.startswith('http://testserver'):
                        entry = entry.replace('http://testserver', '')
                    _value.append(entry)
                value = _value

            if isinstance(payload[field],
                          (six.PY3 and (_io.TextIOWrapper,
                                        _io.BufferedReader) or file)):
                # remove uploaded files
                if six.PY3:
                    file_path = os.path.join(
                        settings.MEDIA_ROOT,
                        value.replace('/uploads/', '')
                    )
                    self.assertFileExists(file_path)
                    os.unlink(file_path)
                elif six.PY2:
                    self.assertFileExists(value)
                    os.unlink(
                        os.path.join(settings.MEDIA_ROOT, value)
                    )
                else:
                    raise EnvironmentError("Wrong python version")
                #: ignore file/image upload case
                continue
            if value != payload.get(field):
                errors.append(
                    '%r: %r != %r' % (field, value, payload[field])
                )
        if errors:
            raise AssertionError(errors)


class ApiTestCaseSet(object):
    model_class = None
    url_prefix = 'api'
    post_format = 'json'
    put_format = None
    pk_value = 1

    LOG_API_STATUSES = [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        status.HTTP_403_FORBIDDEN
    ]

    def get_url_scheme(self, method='detail', url_prefix=None):
        url_prefix = url_prefix or self.url_prefix
        return '%(prefix)s:%(model)s-%(method)s' % {
            'prefix': url_prefix or 'api',
            'model': self.model_class._meta.model_name,
            'method': method
        }

    @staticmethod
    def log_api_errors(response,
                       statuses=LOG_API_STATUSES):
        if response.status_code in statuses:
            json_response = json.loads(response.content)
            for key, item in json_response.items():
                if isinstance(item, (tuple, list)):
                    logging.info("%s: " % key + ", ".join(item))
                else:
                    logging.info(item)

    def setUp(self):
        self.maxDiff = None
        # update content types

        self.owner_field = 'owner'

        self.user = User.objects.get(username='user')
        self.user_password = '123456'
        self.admin = User.objects.get(username='admin')
        self.admin_password = '123456'
        self.other_user = User.objects.get(username='user2')
        self.other_user_password = '123456'

        self.object_instance = self.model_class.objects.get(pk=self.pk_value)
        self.url_detail = reverse(
            self.get_url_scheme(), args=(self.object_instance.pk, ))

        self.url_list = reverse(self.get_url_scheme(method='list'))
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.owner_restrict_delete = False

        self.put = {

        }
        self.patch = {
        }
        self.post = {
        }
        self.object_detail_response = {
        }
        self.object_anonymous_detail_response = None
        self.object_admin_detail_response = None


class ApiAnonymousUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin,
                                    ApiTestSourceAssertionMixin):
    """ ApiAnonymousUserTestCaseMixin

    Anonymous user can perform GET access detail/list, otherwise read only

    .. note::

        anonymous user can access freely for GET method, with restricted output
        data in result which should be configurated by ModelViewSet
        serializer_class property
    """
    def test_get_detail(self):
        response = self.client.get(self.url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        detail_response = (
            self.object_anonymous_detail_response or
            self.object_detail_response)
        self.assertEqual(detail_response, load)

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['count'],
                         self.model_class.objects.count())

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format=self.put_format or self.post_format)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format=self.post_format)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))


class ApiAdminUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin,
                                ApiTestSourceAssertionMixin):
    """
    admin users can claim access for any instance of model
    """
    def test_get_detail(self):
        self.login(self.admin.username, self.admin_password)
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            self.object_admin_detail_response or self.object_detail_response,
            load
        )

    def test_get_list(self):
        self.login(self.admin.username, self.admin_password)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], self.model_class.objects.count())

    def test_put_detail(self):
        self.login(self.admin.username, self.admin_password)
        count = self.model_class.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format=self.put_format or self.post_format)
        self.log_api_errors(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)

        put = dict(**self.put)
        # self.check_response(json_response, put)
        self.assertUpdate(json_response, put)

        self.assertEqual(self.model_class.objects.count(), count)

    def test_post_list(self):
        self.login(self.admin.username, self.admin_password)
        count = self.model_class.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format=self.post_format)
        self.log_api_errors(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_response = json.loads(response.content)

        self.assertEqual(self.model_class.objects.count(), count + 1)
        self.check_response(json_response, self.post)

    def test_patch_detail(self):
        self.login(self.admin.username, self.admin_password)
        count = self.model_class.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.log_api_errors(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        obj = self.model_class.objects.get(pk=self.object_instance.pk)
        self.check_instance(obj, json_response, self.patch)
        self.assertEqual(self.model_class.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = self.model_class.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.log_api_errors(response)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.model_class.objects.count(), count - 1)


class ApiUserOwnerTestCaseMixin(ApiTestCaseSet, TestHelperMixin,
                                ApiTestSourceAssertionMixin):
    """
    owners of their instances could process update (sometimes delete) actions
    """
    def test_get_detail(self):
        self.login(self.user.username, self.user_password)
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response_json, self.object_detail_response)

    def test_get_list(self):
        self.login(self.user.username, self.user_password)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response_json['count'],
                         self.model_class.objects.count())

    def test_put_detail(self):
        self.login(self.user.username, self.user_password)
        count = self.model_class.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format=self.post_format or self.put_format)
        self.log_api_errors(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.check_response(response_json, self.put)
        self.assertEqual(self.model_class.objects.count(), count)

    def test_post_list(self):
        self.login(self.user.username, self.user_password)
        count = self.model_class.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format=self.post_format or self.put_format)
        self.log_api_errors(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_json = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(self.model_class.objects.count(), count + 1)
        self.check_response(response_json, post)

    def test_patch_detail(self):
        self.login(self.user.username, self.user_password)
        count = self.model_class.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.log_api_errors(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        obj = self.model_class.objects.get(pk=self.object_instance.pk)
        self.check_instance(obj, response_json, self.patch)
        self.assertEqual(self.model_class.objects.count(), count)

    def test_delete_detail(self):
        self.login(self.user.username, self.user_password)
        count = self.model_class.objects.count()
        response = self.client.delete(self.url_delete, data={}, format='json')

        # sometimes only admins can delete instances which user owns
        if self.owner_restrict_delete:
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.model_class.objects.count(), count)
            self.assertEqual(
                self.model_class.objects.filter(
                    pk=self.object_instance.pk).exists(),
                True
            )
        else:
            self.log_api_errors(response)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self.model_class.objects.count(), count - 1)


class ApiUserNotOwnerTestCaseMixin(ApiTestCaseSet, TestHelperMixin,
                                   ApiTestSourceAssertionMixin):
    """
    instances with other user (not owner) should have only RO access
    """
    def test_get_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response_json, self.object_detail_response)

    def test_get_list(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response_json['count'],
                         self.model_class.objects.count())

    def test_put_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.put(self.url_put, data=self.put,
                                   format=self.post_format or self.put_format)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)

        self.assertEqual(
            json_response['detail'],
            _('You do not have permission to perform this action.'))

    def test_post_list(self):
        post = dict(**self.post)

        # copy file objects
        for item, value in self.post.items():
            if isinstance(value, six.PY3 and (_io.TextIOWrapper,
                                              _io.BufferedReader) or file):
                post[item] = value
        post.update({
            self.owner_field: self.other_user.get_api_absolute_url(),
        })

        self.login(self.other_user.username, self.other_user_password)
        count = self.model_class.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format=self.post_format or self.put_format)
        self.log_api_errors(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        response_json = json.loads(response.content)

        self.assertEqual(self.model_class.objects.count(), count + 1)
        self.check_response(response_json, post)

    def test_patch_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('You do not have permission to perform this action.'))

    def test_delete_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.delete(self.url_delete, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('You do not have permission to perform this action.'))


class ApiRestrictedAnonymousUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin,
                                              ApiTestSourceAssertionMixin):
    """ ApiAnonymousUserTestCaseMixin

    Anonymous user can not perform GET access detail/list
    either other HTTP

    .. note::

        anonymous user have not access to resource completely, because the
        resource could provide "hidden" or not public data only owner user
        should retrieve
    """
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        response = self.client.get(self.url_detail, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format=self.put_format or self.post_format)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format=self.post_format)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))


class ApiRestrictedOwnerUserTestCaseMixin(ApiUserOwnerTestCaseMixin,
                                          ApiTestCaseSet,
                                          TestHelperMixin,
                                          ApiTestSourceAssertionMixin):
    """
    Can only get access to his own instances, not for everyone else ones
    """
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login(self.user.username, self.user_password)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        kw = {
            self.owner_field: self.user
        }
        qset = Q(**kw)
        self.assertEqual(response_json['count'],
                         self.model_class.objects.filter(qset).count())


class ApiRestrictedUserNotOwnerTestCaseMixin(ApiUserNotOwnerTestCaseMixin,
                                             ApiTestCaseSet,
                                             TestHelperMixin,
                                             ApiTestSourceAssertionMixin):
    """ There's no access for other user resources, we would get 404
    event if resources exists, than we check permission for possibility
    have proceed actions
    """
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        kw = {
            self.owner_field: self.other_user
        }
        qset = Q(**kw)
        self.assertEqual(response_json['count'],
                         self.model_class.objects.filter(qset).count())

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.delete(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.patch(self.url_patch, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))
