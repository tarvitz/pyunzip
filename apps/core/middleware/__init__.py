# coding: utf-8
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from apps.wh.models import UserActivity, GuestActivity, User, Skin,Army, Rank
from django.db.models import Q
from django.contrib import auth
from datetime import datetime
from datetime import timedelta
from apps.core.settings import SETTINGS,ANONYMOUS_SETTINGS
from apps.core.helpers import get_object_or_none, safe_ret
from apps.core.decorators import null

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

class TestMiddleware(object):
    def process_request(self, request):
        request.META['test'] = 'thiz iz da \'est'
    #FIXME: make search replacements!!!
    """
    def process_response(self,request,response):
        if hasattr(request,'session'):
            query = request.session.get('search_q','').lower()
            if ("/search/" in request.get_full_path() and query) or \
            ("/search/" in request.META.get('HTTP_REFERER','')):
                #make replacing more clear and wise
                content = response.content.decode('utf-8','ignore')
                if query in content.lower():
                    content = content.replace(query,"<span style='background-color: white;color: red;'>%s</span>" % query)
                    response.content = content

        return response
    """

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

#obsolete
class UserSettingsMiddleware(object):
    def process_request(self,request):
        from apps.core.models import Settings
        #for user that exists
        if request.user.is_authenticated():
            if not request.user.settings:
                request.user.settings = SETTINGS
                request.user.save()
        #for anonymous users by defaults
        else:
            anonymous_settings = SETTINGS
            anonymous_settings.update(ANONYMOUS_SETTINGS)
            setattr(request.user,'settings',anonymous_settings)

class ChecksMiddleware(object):
    def process_request(self, request):
        #let ie burn in hell
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user = request.user
        if 'msie 6.0' in user_agent.title().lower()\
        or 'msie 7.0' in user_agent.title().lower():
            template = get_template('get_a_working_browser.html')
            html = template.render(Context())
            return HttpResponse(html)
        if  user_agent.title().lower() in (
                'wbsearchbot', 'ahrefsbot/4.0'
            ):
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write('500')
            return response
        if user.is_authenticated() and not user.is_active:
               auth.logout(request)
        if user.is_authenticated():
            """
            if not user.skin:
                user.skin = Skin.objects.get(name__iexact='default')
                #user.skin = Skin.objects.order_by('id')[0]
                user.save()
            """
            if not user.army:
	    	army = get_object_or_none(Army,name__iexact='none')
		if army:
			user.army = army
			user.save()

class BenchmarkingMiddleware(object):
    def process_response(self,request,response):
        if hasattr(requset,'timeit'):
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
