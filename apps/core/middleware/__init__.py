# coding: utf-8
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from apps.wh.models import UserActivity, GuestActivity
from django.contrib import auth
from datetime import datetime
from apps.core.helpers import safe_ret


class BanMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_active:
            try:
                auth.logout(request.user)
            except AttributeError:
                pass


class SetRemoteAddrFromForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            # HTTP_X_FORW can be a comma-separated list of IPs
            real_ip = real_ip.split(',')[0]
            request.META['REMOTE_ADDR'] = real_ip


class UserActivityMiddleware(object):
    def process_request(self, request):
        #if request.user.is_autheticated():
        request.META['HTTP_USER_NICKNAME'] = safe_ret(request, 'user.nickname') or "None"

        u = request.user
        #if registered user ;)
        if u.is_authenticated():
            if not hasattr(u,'useractivity'):
                now = datetime.now()
                ua = UserActivity(user=u, activity_date=now, activity_ip=request.META['REMOTE_ADDR'])
                ua.save()
            if u.is_active:
                now = datetime.now()
                u.useractivity.activity_date = now
                u.useractivity.activity_ip = request.META['REMOTE_ADDR']
                u.useractivity.save()
                #logged in ;)
                u.useractivity.is_logout=False
                u.useractivity.save()
                #purgin this account as being logged as Guest before :) reloggin
                try:
                    guest = GuestActivity.objects.get(activity_ip__exact=request.META['REMOTE_ADDR'])
                    guest.activity_date = None
                    guest.save()
                except GuestActivity.DoesNotExist:
                    pass


class GuestActivityMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            now = datetime.now()
            ip_address = request.META['REMOTE_ADDR']
            try:
                ip_account = GuestActivity.objects.get(activity_ip__exact=ip_address)
                ip_account.activity_date_prev = ip_account.activity_date
                ip_account.activity_date=now
                ip_account.save()
            except GuestActivity.DoesNotExist:
                ip_account = GuestActivity(activity_ip=ip_address,activity_date=now)
                ip_account.save()
        return None


class ChecksMiddleware(object):
    def process_request(self, request):
        # let ie burn in hell
        #user_agent = request.META.get('HTTP_USER_AGENT', '')
        user = request.user
        #if 'msie 6.0' in user_agent.title().lower()\
        #or 'msie 7.0' in user_agent.title().lower():
        #    template = get_template('get_a_working_browser.html')
        #    html = template.render(Context())
        #    return HttpResponse(html)
        #if  user_agent.title().lower() in (
        #        'wbsearchbot', 'ahrefsbot/4.0'
        #    ):
        #    response = HttpResponse()
        #    response['Content-Type'] = 'application/json'
        #    response.write('500')
        #    return response
        if user.is_authenticated() and not user.is_active:
            auth.logout(request)


class BenchmarkingMiddleware(object):
    def process_response(self, request, response):
        if hasattr(request, 'timeit'):
           pass
        return response


class DevMiddleware(object):
    def process_response(self, request, response):
        if request.get_full_path() == reverse('url_login'):
            return response
        if 'dev.' in request.META.get('HTTP_HOST', ''):
            if hasattr(request, 'user'):
                if request.user.has_perm('wh.can_test'):
                    return response
        return HttpResponseRedirect(reverse('url_login'))
