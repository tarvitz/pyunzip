# coding: utf-8

from django.http import HttpResponse
from django.shortcuts import redirect

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


import simplejson as json


def has_permission(perms):
    """checks if request.user has permission"""
    permissions = perms
    
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            perms = user.get_all_permissions()
            if not user.is_active:
                return redirect(reverse('accounts:login'))
            if user.is_superuser:
                return func(request, *args, **kwargs)
            if permissions in [i for i in perms]:
                return func(request, *args, **kwargs)
            else:
                login = reverse('accounts:login')
                return redirect(login)
        return wrapper
    return decorator
