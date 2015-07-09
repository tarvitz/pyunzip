# coding: utf-8

import os
import six

if six.PY3:
    import _io
    file = None

from django.test import TestCase
from apps.core.helpers import (
    post_markup_filter,
)
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from django.db.models import Model, Q
from django.template import Context
from django.template.loader import get_template
from datetime import datetime, date

from rest_framework import status

from django.conf import settings
from copy import deepcopy
User = get_user_model()


import simplejson as json
import allure
from allure.constants import Severity

import logging
logger = logging.getLogger(__name__)


@allure.feature('Core')
class JustTest(TestCase):
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


@allure.feature('Benchmark: Core')
class BenchmarkTemplatesTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json'
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def benchmark(self, template, context=None):
        context = context or {}
        results = []
        for i in range(1000):
            n = datetime.now()
            # if isinstance(template, basestring):
            #     tmpl = Template(template)
            # else:
            #     tmpl = template
            # html = tmpl.render(Context(context))
            offset = datetime.now() - n
            results.append(offset.total_seconds())
        rmin = min(results)
        rmax = max(results)
        avg = sum(results) / len(results)
        logger.info(
            "Got follow timings:\nmin: %(min)s,"
            "\nmax: %(max)s,\navg: %(avg)s" % {
                'min': rmin,
                'max': rmax,
                'avg': avg
            }
        )

    @allure.story('benchmark')
    @allure.severity(Severity.NORMAL)
    def test_benchmark_get_form_tag(self):
        template = """{% load coretags %}
        {% get_form 'apps.comments.forms.CommentForm' as form %}
        <form class='' method='POST'>
        {% csrf_token %}
        {{ form.as_ul }}
        </form>
        """
        self.benchmark(template)

    @allure.story('benchmark')
    @allure.severity(Severity.NORMAL)
    def test_index_page(self):
        for user in ('admin', 'user', None):
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            template = get_template('error_template.html')
            template.render(Context(self.client.request().context))

            logger.info("Testing for '%s': " % user or "Anonymous")
            self.benchmark(
                template,
                self.client.request().context
            )


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
        if not 'form' in context:
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
                })
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
                if '/api/' in value:
                    assertion(response[field], 'http://testserver' + value)
                else:
                    assertion(response[field], value)
            elif isinstance(value, (tuple, list)) and '/api/' in value[0]:
                for item in value:
                    assertion(
                        'http://testserver' + item in response[field],
                        True
                    )
            elif isinstance(value, (six.PY3 and _io.TextIOWrapper or file)):
                # remove uploaded files
                self.assertFileExists(response[field])
                os.unlink(
                    os.path.join(settings.MEDIA_ROOT, response[field])
                )
            else:
                assertion(response[field], value)

    def assertInstance(self, instance, raw):
        """ assert instance fields with raw post data

        :param instance:
        :param (dict) raw: raw post data for instance creation or its update
        :return:
        """

        verify = deepcopy(raw)
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


# Api cases generic access tests
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
                    logger.info("%s: " % key + ", ".join(item))
                else:
                    logger.info(item)

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


# noinspection PyUnresolvedReferences
class ApiAnonymousUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin):
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
        json_response = json.loads(response.content)
        detail_response = (
            self.object_anonymous_detail_response or
            self.object_detail_response)
        self.assertEqual(json_response, detail_response)

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


# noinspection PyUnresolvedReferences
class ApiAdminUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin):
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
            load,
            self.object_admin_detail_response or self.object_detail_response
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

        put = deepcopy(self.put)
        self.check_response(json_response, put)

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


# noinspection PyUnresolvedReferences
class ApiUserOwnerTestCaseMixin(ApiTestCaseSet, TestHelperMixin):
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
        post = deepcopy(self.post)

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


# noinspection PyUnresolvedReferences
class ApiUserNotOwnerTestCaseMixin(ApiTestCaseSet, TestHelperMixin):
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
        post = deepcopy(self.post)

        # copy file objects
        for item, value in self.post.items():
            if isinstance(value, file):
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


class ApiRestrictedAnonymousUserTestCaseMixin(ApiTestCaseSet, TestHelperMixin):
    """ ApiAnonymousUserTestCaseMixin

    Anonymous user can not perform GET access detail/list
    either other HTTP

    .. note::

        anonymous user have not access to resource completely, because the
        resource could provide "hidden" or not public data only owner user
        should retrieve
    """
    def test_get_detail(self):
        response = self.client.get(self.url_detail, follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(
            json_response['detail'],
            _('Authentication credentials were not provided.'))

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


class ApiRestrictedOwnerUserTestCaseMixin(ApiUserOwnerTestCaseMixin,
                                          ApiTestCaseSet,
                                          TestHelperMixin):
    """
    Can only get access to his own instances, not for everyone else ones
    """
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
                                             TestHelperMixin):
    """ There's no access for other user resources, we would get 404
    event if resources exists, than we check permission for possibility
    have proceed actions
    """
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

    def test_get_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))

    def test_delete_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.delete(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))

    def test_patch_detail(self):
        self.login(self.other_user.username, self.other_user_password)
        response = self.client.patch(self.url_patch, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(json_response['detail'],
                         _('Not found'))
