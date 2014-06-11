# coding: utf-8
from django.shortcuts import redirect


class ReadOnlyMiddleware(object):
    def process_request(self, request):
        if (request.method in ('POST', 'PUT', 'PATCH', 'DELETE', )
                and request.user.is_authenticated()):
            user = request.user
            if user.get_active_read_only_policy_warnings().count():
                return redirect('accounts:read-only')