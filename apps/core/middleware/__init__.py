# coding: utf-8
from django.contrib import auth


class BanMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_active:
            auth.logout(request)
