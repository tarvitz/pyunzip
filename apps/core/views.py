# coding: utf-8
import os
from django.http import (
    HttpResponse, )
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.conf import settings

from django.shortcuts import redirect

import logging
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


def robots(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/plain'
    content = open(os.path.join(settings.MEDIA_ROOT, 'robots.txt'), 'r').read()
    response.write(content)
    return response


def index(request):
    return redirect(reverse('pybb:index'))


# CBV Mixins
# noinspection PyUnresolvedReferences
class RequestMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RequestMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs


# noinspection PyUnresolvedReferences
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )


# noinspection PyUnresolvedReferences
class TemplateNamesMixin(object):
    # noinspection PyProtectedMember
    def get_template_names(self):
        """
        :return: list of template names formatted within '_'
        symbols between class words, e.g.
        TestItem binds as test_item
        TestItemStuff binds as test_item_stuff
        """

        if self.template_name:
            return self.template_name

        name = self.model._meta.object_name
        app_label = self.model._meta.app_label
        name = (
            name[0].lower() + "".join(
                ['_' + i if i.isupper() else i for i in name[1:]]
            ).lower()
        )
        template_name = "{app}/{model}{suffix}.html".format(
            app=app_label,
            model=name,
            suffix=self.template_name_suffix or ''
        )

        return [template_name, ]
