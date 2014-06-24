# coding: utf-8
from django.test import TestCase
from apps.core.helpers import (
    post_markup_filter,
) 
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from django.db.models import Model
from django.template import Context, Template
from django.template.loader import get_template
from datetime import datetime, date

from rest_framework import status
from copy import deepcopy
User = get_user_model()

import simplejson as json

import logging
logger = logging.getLogger(__name__)


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json',
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    """ helpers """
    def process_messages(self, instance, kw, fx={}):
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
                print "Could not get url %(user)s in %(url)s, got %(err)s" % msg
            raise AssertionError

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

    def test_css_edit(self):
        pass

    def test_unsubscribe(self):
        pass

    def test_settings(self):
        pass

    def test_settings_store(self):
        pass


class BenchmarkTemplatesTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json'
    ]
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def benchmark(self, template, context={}):
        results = []
        for i in xrange(1000):
            n = datetime.now()
            if isinstance(template, basestring):
                tmpl = Template(template)
            else:
                tmpl = template
            html = tmpl.render(Context(context))
            offset = datetime.now() - n
            results.append(offset.total_seconds())
        rmin = min(results)
        rmax = max(results)
        avg = sum(results) / len(results)
        print "Got follow timings:\nmin: %(min)s,\nmax: %(max)s,\navg: %(avg)s" % {
            'min': rmin,
            'max': rmax,
            'avg': avg
        }
    def test_benchmark_get_form_tag(self):
        template = """{% load coretags %}
        {% get_form 'apps.comments.forms.CommentForm' as form %}
        <form class='' method='POST'>
        {% csrf_token %}
        {{ form.as_ul }}
        </form>
        """
        self.benchmark(template)

    def test_index_page(self):
        for user in ('admin', 'user', None):
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            template = get_template('error_template.html')
            out = template.render(Context(self.client.request().context))

            print "Testing for '%s': " % user or "Anonymous"
            self.benchmark(
                template,
                self.client.request().context
            )


# noinspection PyUnresolvedReferences
class TestHelperMixin(object):
    def login(self, user):
        if user:
            logged = self.client.login(username=user, password='123456')
            self.assertEqual(logged, True)
        else:
            self.client.logout()

    def check_state(self, instance, data, check=lambda x: x, check_in=None):
        messages = []
        check_in = check_in or self.assertIn
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
                print u"Got %(err)s in %(key)s" % msg
            raise AssertionError

    def proceed_form_errors(self, context):
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

        print "Got errors in form:"
        if isinstance(form.errors, dict):
            for key, error_list in form.errors.items():
                print "in '%(key)s' got: '%(errors)s'" % {
                    'key': key,
                    'errors': (
                        "; ".join([unicode(i) for i in error_list])
                        if isinstance(error_list, (list, tuple))
                        else unicode(error_list)
                    )
                }
            return
        elif isinstance(form.errors, (list, tuple)):
            for f in form.errors:
                for key, error_list in f.items():
                    print u"in '%(key)s got: %(errors)s'" % {
                        'key': key, 'errors': "; ".join([
                            unicode(i) for i in error_list])
                    }
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
        assertion = assertion or super(TestHelperMixin, self).assertEqual
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

        :param instance: ModelObject ``instance``
        :param dict response: json serialized api response (dict)
        :param dict data: post/put/patch send data
        :keyword assertion: callable assert function for check data
        :return: None
        """
        assertion = assertion or super(TestHelperMixin, self).assertEqual
        for field, value in data.items():
            if isinstance(value, (datetime, )):
                assertion(response[field], value.isoformat()[:-3])
            elif isinstance(value, date):
                assertion(response[field], value.isoformat())
            elif isinstance(value, basestring):
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
                self.assertIn(obj_item, getattr(instance, field.name).all())

        for key, value in verify.items():
            self.assertEqual(getattr(instance, key), value)


# Api cases generic access tests
class ApiTestCaseSet(object):
    model_class = None
    url_prefix = 'api'

    def get_url_scheme(self, method='detail', url_prefix=None):
        url_prefix = url_prefix or self.url_prefix
        return '%(prefix)s:%(model)s-%(method)s' % {
            'prefix': url_prefix or 'api',
            'model': self.model_class._meta.model_name,
            'method': method
        }

    def setUp(self):
        self.maxDiff = None
        # update content types

        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.object_instance = self.model_class.objects.get(pk=1)
        self.url_detail = reverse(
            self.get_url_scheme(), args=(self.object_instance.pk, ))

        self.url_list = reverse(self.get_url_scheme(method='list'))
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {

        }
        self.patch = {
        }
        self.post = {
        }
        self.object_detail_response = {
        }


# noinspection PyUnresolvedReferences
class ApiAnonymousUserTestCaseMixin(ApiTestCaseSet):
    """
    anonymous user can perform GET access detail/list, otherwise read only
    """
    def test_get_detail(self):
        response = self.client.get(self.url_detail, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], self.model_class.objects.count())

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put, format='json')
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


# noinspection PyUnresolvedReferences
class ApiAdminUserTestCaseMixin(ApiTestCaseSet):
    """
    admin users can clain access for any instance of model
    """
    def test_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], self.model_class.objects.count())

    def test_put_detail(self):
        self.login('admin')
        count = self.model_class.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        put = deepcopy(self.put)
        self.check_response(load, put)

        self.assertEqual(self.model_class.objects.count(), count)

    def test_post_list(self):
        self.login('admin')
        count = self.model_class.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            load = json.loads(response.content)
            for key, item in load.items():
                if isinstance(item, (tuple, list)):
                    logger.info("%s: " % key + ", ".join(item))
                else:
                    logger.info(item)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(self.model_class.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('admin')
        count = self.model_class.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            load = json.loads(response.content)
            for key, item in load.items():
                if isinstance(item, (tuple, list)):
                    logger.info("%s: " % key + ", ".join(item))
                else:
                    logger.info(item)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = self.model_class.objects.get(pk=self.object_instance.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(self.model_class.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = self.model_class.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            load = json.loads(response.content)
            for key, item in load.items():
                if isinstance(item, (tuple, list)):
                    logger.info("%s: " % key + ", ".join(item))
                else:
                    logger.info(item)
        self.assertEqual(self.model_class.objects.count(), count - 1)