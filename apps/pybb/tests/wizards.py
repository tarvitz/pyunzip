# coding: utf-8
from django.test import TestCase
from apps.core.tests import TestHelperMixin
from apps.pybb.models import Poll, PollItem, PollAnswer
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _


__all__ = ['SimpleTest', ]


class SimpleTest(TestCase):
    def test_simple(self):
        self.assertEqual(2, 1 + 1)

# TODO: remote, not usable
class PollWizardTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_pybb_categories.json',
        'tests/fixtures/load_forums.json',
        'tests/fixtures/load_topics.json',
    ]
    items_count = 5
    wizard_step_1_data = {
        'add_poll_wizard-current_step': u'0',
    }
    wizard_step_data = (
        {
            '0-title': u'Сколько бит в байте?',
            '0-items_amount': items_count,
            '0-is_multiple': True,
            'add_poll_wizard-current_step': '0',
        },
        {
            '1-INITIAL_FORMS': '0',
            '1-TOTAL_FORMS': '5',
            '1-MAX_NUM_FORMS': '0',
            '1-0-title': u'пять',
            '1-1-title': u'девять',
            '1-2-title': u'шесть',
            '1-3-title': u'семь',
            '1-4-title': u'восемь',
            'add_poll_wizard-current_step': '1',
        }
    )

    def setUp(self):
        self.wizard_url = reverse_lazy('pybb_poll_add', args=(1, ))

    def test_initial_call(self):
        self.login('user')
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)

        self.assertEqual(wizard['steps'].current, '0')
        self.assertEqual(wizard['steps'].step0, 0)
        self.assertEqual(wizard['steps'].step1, 1)
        self.assertEqual(wizard['steps'].last, '1')
        self.assertEqual(wizard['steps'].prev, None)
        self.assertEqual(wizard['steps'].next, '1')
        self.assertEqual(wizard['steps'].count, 2)

    def test_form_post_error(self):
        self.login('user')
        response = self.client.post(
            self.wizard_url,
            self.wizard_step_1_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['wizard']['steps'].current, u'0'
        )
        self.assertEqual(
            response.context['wizard']['form'].errors,
            {
                'title': [unicode(_('This field is required.'))],
                'items_amount': [unicode(_('This field is required.'))],
            }
        )

    def test_form_post_success(self):
        self.login('user')
        response = self.client.post(
            self.wizard_url, self.wizard_step_data[0],
            follow=True
        )
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, '1')
        self.assertEqual(wizard['steps'].step0, 1)
        self.assertEqual(wizard['steps'].prev, '0')
        self.assertEqual(wizard['steps'].next, None)

    def test_form_stepback(self):
        self.login('admin')
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, '0')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, '1')

        response = self.client.post(
            self.wizard_url, {
                'wizard_goto_step': response.context['wizard']['steps'].prev
            }, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, '0')

    def test_template_context(self):
        self.login('user')
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, '0')
        self.assertEqual(response.context[0].get('another_var', None), None)
        response = self.client.post(self.wizard_url, self.wizard_step_data[0],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].current, '1')
        form = response.context_data['wizard']['form']
        self.assertEqual(response.context_data['form'], form)

    def test_cleaned_data(self):
        self.login('user')
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[0],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(
            context['wizard']['form'].errors,
            []
        )
        response = self.client.post(self.wizard_url, self.wizard_step_data[1],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertNotIn('wizard', context)

    def test_post_items_form_amount(self):
        """test for proper PollItem formset step 2 amount. PollItem formset
        step amount sets in step 1.
        """
        self.login('user')
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.wizard_url, self.wizard_step_data[0],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(
            context['wizard']['form'].errors,
            []
        )
        formset = context['wizard']['form']
        self.assertEqual(len(formset.forms), self.items_count)

    def test_form_finish(self):
        self.login('user')

        poll_count = Poll.objects.count()
        poll_items_count = PollItem.objects.count()
        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(response.context['wizard']['steps'].current, '0')

        response = self.client.post(self.wizard_url, self.wizard_step_data[0],
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(response.context['wizard']['steps'].current, '1')

        response = self.client.post(self.wizard_url, self.wizard_step_data[1],
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            poll_count + 1, Poll.objects.count()
        )
        self.assertEqual(
            poll_items_count + self.items_count,
            PollItem.objects.count()
        )