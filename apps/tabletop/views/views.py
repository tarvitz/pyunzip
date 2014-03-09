# Create your views here.
# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from apps.tabletop.models import (
    Roster, Mission, Game, BattleReport, Codex
)
from apps.tabletop.forms import AddRosterForm,DeepSearchRosterForm,\
    AddBattleReportForm, AddBattleReportModelForm, AddCodexModelForm,\
    AddRosterModelForm
from django.core.paginator import InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.core.helpers import (
    get_settings, get_comments, get_content_type,
    get_object_or_none, paginate, can_act, render_to,
    safe_ret, get_int_or_zero
)
from apps.tracker.decorators import mark_read
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from apps.core import pages, get_skin_template
from apps.core.forms import CommentForm, SphinxSearchForm
#from django.views.generic.simple import direct_to_template
from apps.core.shortcuts import direct_to_template
from django.contrib.contenttypes.models import ContentType
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseServerError,
    Http404
)
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.db.models import Q
from apps.core.decorators import benchmarking, has_permission, \
    lock_with_dev as unlock_for
from apps.core.forms import ApproveActionForm, action_formset_ng
from apps.core import benchmark
from apps.wh.models import Side
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.models import Comment
# -- helpers
from apps.tabletop.helpers import process_roster_query
from django.core import serializers
import simplejson as json
from django.core.cache import cache

from datetime import datetime


@login_required
@benchmarking
@render_to('reports.html')
def reports(request):
    reports = request.user.battle_report_set.all()
    page = get_int_or_zero(request.GET.get('page')) or 1
    reports = paginate(reports, page, pages=settings.OBJECTS_ON_PAGE)
    form = AddBattleReportForm()
    return {
        'reports': reports,
        'form': form
    }

@benchmarking
@render_to('reports/reports.html')
def battle_reports(request):
    page = get_int_or_zero(request.GET.get('page', 1)) or 1
    can_edit = request.user.has_perm('tabletop.edit_battle_report')
    kw = {}
    if not can_edit:
        kw.update({'approved': True})
    reports = paginate(
        BattleReport.objects.filter(**kw), page, pages=settings.OBJECTS_ON_PAGE
    )
    return {
        'reports': reports
    }


@render_to('reports/report.html')
@mark_read(object_pk='pk', app='tabletop', module='BattleReport')
def report(request, pk):
    can_edit = False
    if request.user.is_authenticated():
        can_edit = request.user.has_perm('tabletop.edit_battle_report')
    kw = {'pk': pk}
    if not can_edit:
        kw.update({'approved': True})
    report = cache.get('tabletop:report:%s' % pk)
    if not report:
        report = get_object_or_404(BattleReport, **kw)
        cache.set('tabletop:report:%s' % report.pk, report)
    else:
        if not can_edit and not report.approved:
            raise Http404("Not allowed")
    # make more generic ? :)
    ct = ContentType.objects.get(
        app_label=report._meta.app_label,
        model=report._meta.module_name
    )
    comments = Comment.objects.filter(content_type=ct, object_pk=str(report.pk))
    comments_on_page = settings.OBJECTS_ON_PAGE
    page = get_int_or_zero(request.GET.get('page', 1)) or 1
    #if request.user.is_authenticated():
    #    comments_on_page = request.user.settings.get(
    #        'comments_on_page', settings.OBJECTS_ON_PAGE
    #    )
    comments = paginate(
        comments, page,
        pages=comments_on_page
    )
    return {'report': report, 'comments': comments}

@login_required
@render_to('reports/report.html')
def report_approve(request, pk, approved=True):
    can_edit = request.user.has_perm('tabletop.edit_battle_report')
    if not can_edit:
        raise Http404("hands off")
    report = get_object_or_404(BattleReport, pk=pk)
    report.approved = approved
    report.save()
    return {
        'redirect': 'tabletop:report',
        'redirect-args': (report.id, )
    }

@unlock_for({'DEVELOPMENT': True})
@benchmarking
@csrf_protect
def index(request):
    template = get_skin_template(request.user,'battle_report_index.html')
    battlereps = BattleReport.objects.all()
    _pages_ = get_settings(request.user,'objects_on_page',20)
    page = request.GET.get('page',1)
    formclass = action_formset_ng(request, battlereps, BattleReport,
        permissions=['tabletop.delete_battlereport', 'tabletop.change_battlereport'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(reverse('tabletop:battle-report'))
        else:
            return direct_to_template(request, template,
                {'battlereps': battlereps,
                'form': form}, processors=[benchmark])
    form = formclass()
    battlereps = paginate(battlereps,page,pages=_pages_)
    return direct_to_template(request, template,
        {'battlereps': battlereps,
        'form': form},
        processors=[benchmark])

@benchmarking
@unlock_for({'DEVELOPMENT': True})
def show_battle_report(request,id):
    template = get_skin_template(request.user,'battle_report.html')
    battle_report = get_object_or_404(BattleReport,id=id)
    comments = get_comments(BattleReport,object_pk=str(id))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    page = request.GET.get('page',1)
    comments = paginate(comments,page,pages=_pages_,jump='#comments')

    ct = get_content_type(BattleReport)
    #kind a huge one, we need to cut it up ^^
    #upd: we 'ud it up!
    form = CommentForm(request=request,initial={'app_n_model':'tabletop.battlereport','obj_id': id,'url':
                request.META.get('PATH_INFO','')})
    return render_to_response(template,
        {
            'battle_report':battle_report,
            'comments':comments,
            'form': form,
        },context_instance=RequestContext(request,processors=[benchmark])
    )

@benchmarking
def index_rosters(request):
    template = get_skin_template(request.user,'user_rosters.html')
    rosters = Roster.objects.all()
    _pages_ = get_settings(request.user,'rosters_on_page',20)
    page = request.GET.get('page',1)
    formclass = action_formset_ng(request, rosters, Roster,
        permissions=['tabletop.change_roster', 'tabletop.delete_roster'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(reverse('tabletop:rosters'))
        else:
            return direct_to_template(request, template,
                {'rosters': rosters, 'form': form},
                processors=[benchmark])
    rosters = paginate(rosters,page,pages=_pages_)
    form = formclass()
    return direct_to_template(request, template,
        {'rosters': rosters, 'form': form},
        processors=[benchmark])
    #render_to_response(template,{'rosters':rosters},
    #    context_instance=RequestContext(request,processors=[benchmark]))

@login_required
@benchmarking
def user_rosters(request,nickname='', pts=''):
    kw = dict()
    #if race and 'all' not in race : kw.update({'race__name__iexact': race })
    #elif race and 'all' in race: pass

    if pts: kw.update({'pts':pts})
    
    if not nickname: 
        user = request.user
    else:
        user = get_object_or_404(User,nickname__iexact=nickname)
    show_deleted = get_settings(request.user,'show_deleted_rosters',False)
    if not show_deleted: kw.update({'is_orphan': False})

    template = get_skin_template(request.user,'user_rosters.html')
    _pages_ = get_settings(request.user, 'objects_on_page',20)
    if nickname:    qset_nicks = Q(owner=user)|Q(user=user)|Q(player__iexact=user.nickname)
    elif not nickname and pts: qset_nicks = Q()
    else: qset_nicks = Q(owner=request.user)
    rosters = Roster.objects.filter(qset_nicks,Q(**kw))
    page = request.GET.get('page',1)
    formclass = action_formset_ng(request, rosters, Roster,
        permissions=['tabletop.delete_roster', 'tabletop.change_roster'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(reverse('tabletop:rosters'))
        else:
            return direct_to_template(request, template,
                {'rosters': rosters, 'form': form},
                processors=[benchmark])
    form = formclass()
    rosters = paginate(rosters,page,pages=_pages_)
    return direct_to_template(request, template,
        {'rosters': rosters, 'form': form},
        processors=[benchmark])
    #render_to_response(template,{'rosters': rosters},
        #context_instance=RequestContext(request,processors=[benchmark]))

@login_required
@benchmarking
def codex_rosters(request, id, revision):
    template = get_skin_template(request.user, 'user_rosters.html')
    codex = get_object_or_404(Codex, id=id)
    rosters = Roster.objects.filter(codex=codex)
    page = request.GET.get('page', 1)
    _pages_ = get_settings(request.user, 'rosters_on_page', 20)
    formclass = action_formset_ng(request, rosters, Roster,
        permissions=['tabletop.delete_roster', 'tabletop.change_roster'])
    if request.method == 'POST':
        form = formclass(request.POST)
        if form.is_valid():
            qset = form.act(form.cleaned_data['action'],
                form.cleaned_data['items'])
            if 'response' in qset: return qset['response']
            return HttpResponseRedirect(reverse('reverse:rosters'))
        else:
            return direct_to_template(request, template,
                {'rosters': rosters, 'form': form},
                processors=[benchmark])
    form = formclass()
    rosters = paginate(rosters, page, pages=_pages_)
    return direct_to_template(request, template, {'rosters': rosters, 'form': form},
        processors=[benchmark])

@benchmarking
def search_rosters(request):
    template = get_skin_template(request.user,'search_rosters.html')
    kw = dict()
    kw_own = dict()
    roster_query = None
    if 'roster_query' in request.session:
        if reverse('tabletop:rosters-search') == request.get_full_path():
            del request.session['roster_query']
        else:
            roster_query = request.session.get('roster_query',None)
    if request.method == 'POST':
        form = DeepSearchRosterForm(request.POST,request=request)
        if form.is_valid():
            player = form.cleaned_data['player']
            title = form.cleaned_data['title']
            race = form.cleaned_data['race']
            raw_pts = form.cleaned_data['pts']
            import re
            r = re.compile('(<|>|>=|<=|==|)(\d{1,5})')
            #>,1000 for example :)
            try:
                sign,pts = r.findall(raw_pts)[0]
            except (IndexError):
                sign,pts = None,None
               
            roster_query = {'player': player, 'title': title, 'race':race,'pts':pts,'pts_sign':sign}
            #print roster_query
            request.session['roster_query'] = roster_query
            #processing query with helper-function
            qset = process_roster_query(roster_query)
            #getting da rosters 
            #rosters = Roster.objects.filter(qset_nicks,qset,qset_race)
            rosters = Roster.objects.filter(*qset)
            #print rosters,"\n" 
            #print "first call: ",qset_nicks,qset
            _pages_ = get_settings(request.user,'rosters_on_page',20)
            page = request.GET.get('page',1)
            rosters = paginate(rosters,page,pages=_pages_)

            return render_to_response(template,{'rosters':rosters,'form':form,'query':True},
                context_instance=RequestContext(request,processors=[benchmark]))
        else:                    
            return render_to_response(template,{'form':form,'query':False},
                context_instance=RequestContext(request,processors=[benchmark]))
    else:
        rosters = None
        form = DeepSearchRosterForm()
        if roster_query:
            qset = process_roster_query(roster_query)
            #getting the rosters
            rosters = Roster.objects.filter(*qset)
            _pages_ = get_settings(request.user,'rosters_on_page',20)
            page = request.GET.get('page',1)
            rosters = paginate(rosters,page,pages=_pages_)
            form.fields['player'].initial = roster_query['player']
        
            if 'pts_sign' in roster_query:
                form.fields['pts'].initial = "%s%s" % ( roster_query['pts_sign'], roster_query['pts'] )
            else:
                form.fields['pts'].initial = roster_query['pts']

            form.fields['title'].initial = roster_query['title']
            form.fields['race'].initial = roster_query['race']
        return render_to_response(template,{'form':form,'rosters':rosters,'query':roster_query},
            context_instance=RequestContext(request,processors=[benchmark]))

@benchmarking
def sphinx_search_rosters(request):
    template = get_skin_template(request.user, "includes/sphinx_search_roster.html")
    if request.method == 'POST':
        form = SphinxSearchForm(request.POST)
        if form.is_valid():
            rosters = Roster.search.query(form.cleaned_data['query'])
            _pages_ = get_settings(request.user, 'rosters_on_page', 20)
            page = request.GET.get('page', 1)
            rosters = paginate(rosters, page, pages=_pages_)
            return direct_to_template(request, template,
                {'form': form, 'objects': rosters, 'search_query': True},
                processors=[benchmark])
        else:
            return direct_to_template(request, template,
                {'form': form, 'search_query': True}, processors=[benchmark])
    form = SphinxSearchForm()
    return direct_to_template(request, template, {'form': form},
        processors=[benchmark])

@login_required
def unorphan(request,id):
    roster = get_object_or_none(Roster,id=id)
    if roster:
        roster.is_orphan = False
        roster.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
@permission_required('tabletop.delete_roster')
def delete_roster(request,id=None,action=''):
    roster = get_object_or_none(Roster,id__exact=id)
    if roster:
        if request.user.has_perm('purge_roster')\
        or request.user == roster.owner\
        or request.user.is_superuser:
            brs = BattleReport.objects.filter(users=roster)
            if len(brs)>0:
                #unlink owner if there is battlereports
                roster.is_orphan = True
                roster.save()
            else:
                #deletes roster if there's no battelreport mention
                roster.delete()
    #referer = '/roster/purged'
    #deleting via approve_action
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            #todo: make this hotfix more flexible
            referer = reverse('tabletop:rosters')
            #form.cleaned_data['url'] 
    return HttpResponseRedirect(referer)


@login_required
@render_to('add_roster.html', allow_xhr=True)
def action_roster(request, id=None, action=None):
    instance = None
    if id:
        instance = get_object_or_404(Roster, id=id)

    form = AddRosterModelForm(
        request.POST or None, instance=instance,
        request=request
    )

    if request.method == 'POST':
        if form.is_valid():
            #do not let overriding owner
            if not hasattr(form.instance, 'owner'):
                form.instance.owner = request.user
            form.save()
            return {
                'redirect': 'tabletop:roster',
                'redirect-args': (form.instance.pk,)
            }
    return {
        'form': form
    }


@login_required
def action_roster_old(request, id=None, action=''):
    template = get_skin_template(request.user,'add_roster.html')
    if request.method == 'POST':
        form = AddRosterForm(request.POST,request=request)
        if form.is_valid():
            title = form.cleaned_data['title']
            roster_text = form.cleaned_data['roster']
            syntax = form.cleaned_data['syntax']
            comments = form.cleaned_data['comments']
            race_raw = int(form.cleaned_data['race'])
            player = form.cleaned_data['player']
            custom_race = form.cleaned_data['custom_race']
            pts = form.cleaned_data['pts']
            user = get_object_or_none(User,nickname__iexact=player)
            referer = form.cleaned_data['referer']

            if not user: roster_user = None
            else: roster_user = user
            race = get_object_or_none(Side,id__exact=int(race_raw))
            
            if action == 'edit': #edit roster
                roster = get_object_or_none(Roster,id__exact=id)
                if roster:
                #replace it with more clear and brilliant code
                    roster.title = title
                    roster.syntax = syntax
                    roster.comments = comments
                    roster.race = race
                    #roster.user = roster_user
                    roster.pts = pts
                    roster.custom_race = custom_race
                    roster.player = roster.player
                    roster.roster = roster_text
                    if request.user == roster.user:
                        #print request.user, roster.user,": o_O"
                        roster.owner = request.user
                    roster.save()
                else:
                    return HttpResponseRedirect('/roster/does/not/exists')

            else:
                kw = {}
                if roster_user: kw.update({'user':roster_user})
                else: kw.update({'player':player})
                roster = Roster(title=title,roster=roster_text,syntax=syntax,comments=comments,
                    race=race,custom_race=custom_race,pts=pts,owner=request.user,**kw)
            roster.save()
            return HttpResponseRedirect(referer)
        else:
            return direct_to_template(request,template,{'form':form})
    else:
        form = AddRosterForm(request=request)
        referer = request.META.get('HTTP_REFERER','/')
        form.fields['referer'].initial = referer
        
        roster = get_object_or_none(Roster,id__exact=id)
        #action edit
        if action == 'edit':
            if roster:
                if roster.user == request.user or \
                    roster.owner == request.user or \
                    request.user.has_perm('tabletop.edit_anonymous_rosters') or\
                    request.user.has_perm('tabletop.edit_user_rosters') or\
                    request.user.is_superuser:
                    for i in ['title','roster','comments','custom_race','player','pts']:
                        form.fields[i].initial = getattr(roster,i)
                    form.fields['syntax'].initial = roster.syntax
                    if hasattr(roster.race,'id'): form.fields['race'].initial = str(roster.race.id)
                else:
                    return HttpResponseRedirect('/permission/denied/')
            else:
                return HttpResponseRedirect('/roster/does/not/exists')
        #end action edit
        #action spawn
        if action == 'spawn':
            if roster:
                if roster.user == request.user and\
                    roster.owner != request.user:
                        roster.owner = roster.user
                        roster.save()
                        #url = reverse('url_user_rosters',None)
                        url = request.META.get('HTTP_REFERER','/')
                        return HttpResponseRedirect(url)
                else:
                    return HttpResponseRedirect('/permission/denied/')
    return direct_to_template(request,template,{'form':form})

@benchmarking
def show_roster(request,id):
    roster = get_object_or_404(Roster,id=id)
    template = get_skin_template(request.user, 'roster.html')
    #should we implement functionallity to support
    #comments within rosters?
    ct = get_content_type(Roster)
    comments = get_comments(Roster,object_pk=str(id))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    page = request.GET.get('page',1)
    comments = paginate(comments,page,pages=_pages_,jump='#comments')

    form = CommentForm(request=request,initial={'app_n_model':'tabletop.roster','obj_id': id,'url':
                request.META.get('PATH_INFO','')})

    return render_to_response(template,
        {'roster':roster,'form':form,'comments':comments},
        context_instance=RequestContext(request,processors=[benchmark]))

#obsolete
@login_required
@can_act
def add_old_battle_report(request,id=None,action=''):
    template = get_skin_template(request.user,'add_battle_report.html')
    if request.method == 'POST':
        referer = request.META.get('HTTP_REFERER','/')
        form = AddBattleReportForm(request.POST,request=request)
        if form.is_valid():
            title = form.cleaned_data['title']
            rosters = form.cleaned_data['rosters'] #list of int
            winner = form.cleaned_data['winner'] #roster instance
            mission = form.cleaned_data['mission'] #mission instance
            layout = form.cleaned_data['layout'] 
            syntax = form.cleaned_data['syntax']
            comment = form.cleaned_data['comment']
            next = form.cleaned_data['next']
            published = datetime.now()
            ip_address = request.META.get('REMOTE_ADDR',None)
            
            if action == 'edit':
                map = ['title','mission','layout','syntax','comment',
                    'winner']
                br = get_object_or_none(BattleReport,id=id)
                if not br:
                    return HttpResponseRedirect('/report/does/not/exist')
                for m in map: setattr(br,m,locals()[m])
                br.clean_rosters()
                for rst in rosters:
                    r = get_object_or_none(Roster,id=rst)
                    if r:
                        br.users.add(r)
                    else:
                        return HttpResponseRedirect('/report/rosters/broken/')
                br.save()
                return HttpResponseRedirect(next)
            #create new one
            else:
                #approved = True by default
                br = BattleReport(owner=request.user,title=title,winner=winner,
                    mission=mission,layout=layout,syntax=syntax,comment=comment,
                    published=published,ip_address=ip_address,approved=True)
                br.save()
                for rst in rosters:
                    r = get_object_or_none(Roster,id=rst)
                    if r:
                        br.users.add(r)
                    else:
                        br.delete() #deletes before its broken
                        return HttpResponseRedirect('/report/rosters/broken/')
                br.save()
                return HttpResponseRedirect(next)
        else:
            #print "form is invalid",form.errors
            return direct_to_template(request,template,{'form':form})
    
    form = AddBattleReportForm(request=request)
    form.fields['next'].initial = request.META.get('HTTP_REFERER','/')
    if action == 'edit': #lets go fieled the form :)
        br = get_object_or_none(BattleReport,id=id)
        if br:
            map = ['title','layout','comment']
            for m in map:
                form.fields[m].initial = getattr(br,m)
            rosters = str([i.id for i in br.users.distinct().order_by('id')])
            import re
            form.fields['rosters'].initial = ",".join(re.findall(r'\d+',rosters))
            form.fields['winner'].initial = br.winner.id
            form.fields['syntax'].initial = br.syntax
            form.fields['mission'].initial = br.mission.id
        else:
            return HttpResponseRedirect('/report/doest/not/exist/')
    return direct_to_template(request,template,{'form':form})

#@todo: may be should be MORE CLEAN?
@unlock_for({'DEVELOPMENT': True})
@login_required
@can_act
def add_battle_report(request, action=None, id=None):
    template = get_skin_template(request.user, 'add_battle_report.html')
    br = None
    if action == 'edit':
        br = get_object_or_404(BattleReport, id=id)
    if request.method == 'POST':
        form = AddBattleReportModelForm(request.POST, request=request, instance=br)
        if form.is_valid():
            instance = form.instance
            instance.owner = request.user
            instance.published = datetime.now()
            instance.approved = True
            instance.ip_address = request.META.get('REMOTE_ADDR','127.0.0.1')
            form.save()
            return HttpResponseRedirect(reverse('tabletop:battle-report'))
        else:
            return direct_to_template(request, template, {'form': form})
    form = AddBattleReportModelForm(instance=br)
    return direct_to_template(request, template, {'form': form})

@login_required
@render_to('reports.html', allow_xhr=True)
def report_add(request, pk=None):
    instance = None
    can_edit = request.user.has_perm('tabletop.edit_battle_report')

    if pk:
        instance = get_object_or_404(BattleReport, pk=pk)
        if not can_edit and request.user != instance.owner:
            raise Http404("hands off")
    form = AddBattleReportForm(
        request.POST or None,
        instance=instance, request=request)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            # reloading wins/defeats
            if instance.approved:
                instance.save()
            #for roster in instance.rosters.all():
            #    roster.reload_wins_defeats(save=True)
            return {'redirect': 'tabletop:battle-reports'}
    return {'form': form}

@login_required
def xhr_rosters(request, search):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    queryset = (Q(title__icontains=search) | Q(owner__nickname__icontains=search)
        | Q(pts__icontains=search)
        | Q(codex__title__icontains=search)
        | Q(codex__plain_side__icontains=search)
        | Q(custom_codex__icontains=search)
        | Q(player__icontains=search)
    )
    rosters = Roster.objects.filter(queryset)
    lw_rosters = list()
    raw = [ (r.pk, r.__unicode__()) for r in rosters ]
    lw_rosters = [ {'pk': r[0], 'title': r[1] } for r in raw ]
    #response.write(serializers.serialize("json",lw_rosters))
    if lw_rosters> 20:
        lw_rosters = lw_rosters[:20]
    response.write(json.dumps(lw_rosters))
    return response

def xhr_get_roster(request, id):
    from apps.news.templatetags.newsfilters import  bbfilter
    from apps.core.helpers import post_markup_filter, render_filter
    from django.utils.safestring import mark_safe
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    roster = get_object_or_none(Roster, id=id)
    if roster:
        roster.roster = render_filter(
            post_markup_filter(roster.roster),
            roster.syntax or 'textile'
        )
        response.write(serializers.serialize("json", [roster]))
    else:
        response.write("[]")
    return response

def xhr_get_codex_revisions(request, id=None):
    response = HttpResponse()
    response['Content-Type'] = 'text/javascript'
    codex = get_object_or_none(Codex, id=id)
    if codex:
        response.write(json.dumps(
            {
                'revisions': codex.revisions,
                'revlist': [int(i) for i in codex.revisions.split(',')],
            }
        ))
    else:
        response.write('[]')
    return response

@unlock_for({'DEVELOPMENT': True})
@login_required
@can_act
def delete_battle_report(request,id,approve=''):
    br = get_object_or_none(BattleReport,id=id)
    if br.owner == request.user or request.user.is_superuser or\
        request.user.has_perm('tabletop.delete_battlereports'):
        if br:
            br.delete()
            return HttpResponseRedirect(reverse('tabletop:battle-report'))
        else:
            return HttpResponseRedirect('/report/doest/not/exist')
    else:
        return HttpResponseRedirect('/permission/denied')
    return HttpResponseRedirect(reverse('tabletop:battle-report'))

@csrf_protect
@login_required
@has_permission('tabletop.add_codex')
def action_codex(request, id=None, action=None):
    template = get_skin_template(request.user, 'add_codex.html')
    instance = None
    if id:
        instance = get_object_or_404(Codex, id=id)
    if request.method == 'POST':
        form = AddCodexModelForm(request.POST, instance=instance)
        if form.is_valid():
            instance = form.instance
            if request.POST['army']:
                instance.content_type = get_content_type('wh.army')
                instance.object_id = int(request.POST['army'])
            else:
                instance.content_type = get_content_type('wh.side')
                instance.object_id = int(request.POST['side'])
            form.save()
            return HttpResponseRedirect(reverse('tabletop:codex', args=(instance.pk,)))
        else:
            return direct_to_template(request, template,
                {'form': form})
    form = AddCodexModelForm(instance=instance)
    return direct_to_template(request, template, {'form': form})

@login_required
def show_codex(request, id):
    template = get_skin_template(request.user, 'show_codex.html')
    codex = get_object_or_404(Codex, id=id)
    return direct_to_template(request, template, {'codex': codex})

@login_required
def show_codexes(request):
    template = get_skin_template(request.user, 'show_codexes.html')
    codexes = Codex.objects.all()
    _pages_ = get_settings(request.user, 'objects_on_page', 20)
    page = request.GET.get('page', 1)
    codexes = paginate(codexes, page, pages=_pages_)
    return direct_to_template(request, template,
        {'codexes': codexes})
