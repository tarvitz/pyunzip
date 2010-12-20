# coding=utf-8

import re
from datetime import datetime, timedelta

from django.http import Http404, HttpResponseNotAllowed, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers       import reverse
from django.http                    import HttpResponseRedirect, \
                                           HttpResponseNotFound
from django.shortcuts               import get_object_or_404, \
                                           render_to_response

from django.contrib.admin.views.decorators import staff_member_required

from django.views.generic.simple    import direct_to_template
from django.template                import RequestContext
from django.utils.translation       import ugettext as _

from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.conf import settings

from utils.paginator import DiggPaginator
from apps.quotes.forms import QueueQuoteForm
from apps.quotes.models import Quote, QueueQuote

#my implements
from apps.core import get_skin_template
from apps.core.helpers import can_act as m_can_act

# this is a decorator for a page views, enabling visitors voting ability
def enable_actions(func):

    def wrapper(request, *args, **kwargs):
        if not request.session.test_cookie_worked(): #.get('can_act', False):
            request.session.set_test_cookie() #['can_act'] = True

        return func(request, *args,**kwargs)

    return wrapper

def can_act(request):
    return request.session.test_cookie_worked() #.get('can_act', False)

def require_actions_permited(func):
    
    def wrapper(request, *args, **kwargs):
        if can_act(request):
            return func(request, *args,**kwargs)
        else:
            return direct_to_template(request, 'errors/cookies.html', {})

    return wrapper

def can_post(request):

    added_ts = request.session.get('last_added', '')
    #-@todo: uncomment
    if request.user.is_staff or added_ts == '':
    #-@todo: comment
    #if added_ts == '':
        return True
    else:
        td = timedelta(minutes=5)
        #added_ts = datetime(*[int(i) for i in re.split('\.|-|:|\ ', added_ts)])

        return (added_ts + td) < datetime.now()

def require_timeout(func):

    def wrapper(*args, **kwargs):
        request = args[0]
        if can_post(request):
            return func(*args,**kwargs)
        else:
            return direct_to_template(request, 'errors/add_timeout.html', {})

    return wrapper

#@enable_actions
#def index_view(request):
#    qList =  Quote.objects.filter(approved=True).order_by('-dateApproved')[:20]
#    return render_to_response('index.html', { 'qList': qList }) #, 'debug': str(dict(request.session)) })

@enable_actions
def index(request, page_number=1):
    template = get_skin_template(request.user,'q_index.html')
    quotes_list = Quote.objects.all()

    try:
        paginator = DiggPaginator(quotes_list, settings.QUOTES_PER_PAGE, body=6, padding=2)
        page = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        raise Http404
        #return HttpResponseNotFound('page not found')

    page.view = 'apps.quotes.views.index'

    return direct_to_template(request, template, { 'page': page })


@enable_actions
def best(request):
    template = get_skin_template(request.user,'best.html')
    quotes =  Quote.objects.order_by('-rate')[:settings.QUOTES_PER_PAGE]
    return direct_to_template(request, template, { 'quotes': quotes })

@enable_actions
def quote(request, id=0):
    template = get_skin_template(request.user,'quote.html')
    quote = get_object_or_404(Quote, pk=id) #, approved=True)
    return direct_to_template(request, template, { 'quote': quote })

@enable_actions
def search(request, page_number=1):
    template = get_skin_template(request.user,'quotes_search.html')
    query = request.POST.get('q', '')

    if request.method == 'POST':
        if query:
            request.session['search_q'] = query
    else:
        if request.get_full_path() == reverse('apps.quotes.views.search'):
            if 'search_q' in request.session:
                del request.session['search_q']
        else:
            query = query or request.session.get('search_q', '')

    if query:
        #qset = (
        #    Q(title__icontains=query) |
        #    Q(authors__first_name__icontains=query) |
        #    Q(authors__last_name__icontains=query)
        #)

        quotes_list = Quote.objects.filter(text__icontains=query).distinct()#[:25]
        try:
            paginator = DiggPaginator(quotes_list, settings.QUOTES_PER_PAGE, body=6, padding=2)
            page = paginator.page(page_number)
            page.view = 'apps.quotes.views.search'
        except (EmptyPage, InvalidPage):
            raise Http404
    else:
        page = None #[]

    return direct_to_template(request, template, {
        'page': page,
        'query': query
    })

#post issues! require_timeout does not work
@enable_actions
@require_actions_permited
@require_timeout
@login_required
@m_can_act
def add(request):
    add_template = get_skin_template(request.user,'q_add.html')
    add_success_template = get_skin_template(request.user,'add_success.html')
    if request.method == 'POST':
        
        form = QueueQuoteForm(request.POST)
        
        if form.is_valid():
            q = form.save(commit=False)
            q.sender_ip = request.META.get('REMOTE_ADDR', '')
            q.save()
            request.session['last_added'] = datetime.now()
            return direct_to_template(request, add_success_template, {})
        else:
            return direct_to_template(request, add_template, { 'form': form })
        
    else:
        return direct_to_template(request, add_template, { 'form': QueueQuoteForm() })

def rss(request):
    quotes =  Quote.objects.order_by('-date_pub')[:settings.QUOTES_PER_PAGE]
    response = direct_to_template(request, 'rss.xml', { 'quotes': quotes })
    response['Content-Type'] = 'text/xml'
    return response


def vote(request, id=0, how=''):
    template = get_skin_template(request.user,'quote.html')
    q = get_object_or_404(Quote, pk=id)

    voted_flag = 'voted_for_q%s' % id

    if can_act(request) and not voted_flag in request.session:
        request.session[voted_flag] = True
        q.rate = (q.rate + 1) if how == 'up' else (q.rate - 1)
        q.save()

    ajax = ( request.META.get('CONTENT_TYPE', '') == 'application/x-www-form-urlencoded' )

    if ajax:
        return HttpResponse(q.rate)
    else:
        return direct_to_template(request, template, { 'quote': q })


@staff_member_required
def queue(request, page_number=1):
    template = get_skin_template(request.user,'queue.html')
    ids = request.user.seen_quotes.values_list('id', flat=True)
    quotes_list = QueueQuote.objects.exclude(id__in=ids).order_by('date_add')

    try:
        paginator = DiggPaginator(quotes_list, settings.QUOTES_PER_PAGE, body=6, padding=2)
    except (EmptyPage, InvalidPage):
        raise Http404

    page = paginator.page(page_number)
    page.view = 'apps.quotes.views.queue'

    return direct_to_template(request, template, { 'page': page })

@staff_member_required
def approve(request, id=0):
    uq = get_object_or_404(QueueQuote, pk=id)
    uq.approve(request.user)
    return HttpResponseRedirect(reverse('apps.quotes.views.queue'))

@staff_member_required
def reject(request, id=0):
    quote = get_object_or_404(QueueQuote, pk=id)
    if request.user not in quote.rejected_by.all():
        quote.rejected_by.add(request.user)
    if request.user not in quote.seen_by.all():
        quote.seen_by.add(request.user)
    #quote.save()
    return HttpResponseRedirect(reverse('apps.quotes.views.queue'))

@staff_member_required
def hide(request, id=0):
    quote = get_object_or_404(QueueQuote, pk=id)
    if request.user not in quote.seen_by.all():
        quote.seen_by.add(request.user)
    #quote.save()
    return HttpResponseRedirect(reverse('apps.quotes.views.queue'))

@staff_member_required
def edit(request, id=0):
    template = get_skin_template(request.user,'queue_quote_edit.html')
    quote = get_object_or_404(QueueQuote, pk=id)

    if request.method=='POST':
        form = QueueQuoteForm(request.POST, { 'pk': id })
        if form.is_valid():
            #form.save()
            quote.text = form.cleaned_data['text']
            quote.save()
            return HttpResponseRedirect(reverse('apps.quotes.views.queue_quote', kwargs={ 'id': id }))
        else:
            return direct_to_template(request, template, { 'quote': quote, 'form': form })
    else:
        form = QueueQuoteForm(initial={ 'text': quote.text })
        return direct_to_template(request, template, { 'quote': quote, 'form': form })


@staff_member_required
def queue_quote(request, id=0):
    template = get_skin_template(request.user,'queue_quote.html')
    quote = get_object_or_404(QueueQuote, pk=id) #, approved=True)
    return direct_to_template(request, template, { 'quote': quote })
