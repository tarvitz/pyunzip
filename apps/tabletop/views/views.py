# coding: utf-8
from apps.tabletop.models import (
    Roster, BattleReport, Codex
)
from apps.tabletop.forms import (
    AddRosterForm,
    AddBattleReportForm, AddBattleReportModelForm, AddCodexModelForm,
    AddRosterModelForm)

from django.core.urlresolvers import reverse
from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.core.helpers import (
    get_comments, get_content_type,
    get_object_or_None, paginate, can_act, render_to, get_int_or_zero
)

from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.core import get_skin_template

from apps.core.shortcuts import direct_to_template
from django.contrib.contenttypes.models import ContentType
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.http import (
    HttpResponse, HttpResponseRedirect,
    Http404
)
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from apps.core.decorators import (
    has_permission
)

from apps.wh.models import Side
from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.models import Comment
from django.views import generic

from django.core import serializers
import simplejson as json
from django.core.cache import cache

from datetime import datetime


@login_required
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


@login_required
def unorphan(request,id):
    roster = get_object_or_None(Roster,id=id)
    if roster:
        roster.is_orphan = False
        roster.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


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
            user = get_object_or_None(User,nickname__iexact=player)
            referer = form.cleaned_data['referer']

            if not user: roster_user = None
            else: roster_user = user
            race = get_object_or_None(Side,id__exact=int(race_raw))
            
            if action == 'edit': #edit roster
                roster = get_object_or_None(Roster,id__exact=id)
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
        
        roster = get_object_or_None(Roster,id__exact=id)
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
                br = get_object_or_None(BattleReport,id=id)
                if not br:
                    return HttpResponseRedirect('/report/does/not/exist')
                for m in map: setattr(br,m,locals()[m])
                br.clean_rosters()
                for rst in rosters:
                    r = get_object_or_None(Roster,id=rst)
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
                    r = get_object_or_None(Roster,id=rst)
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
        br = get_object_or_None(BattleReport,id=id)
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
    roster = get_object_or_None(Roster, id=id)
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
    codex = get_object_or_None(Codex, id=id)
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

@login_required
@can_act
def delete_battle_report(request,id,approve=''):
    br = get_object_or_None(BattleReport,id=id)
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


# cbv
class RostersListView(generic.ListView):
    """ Everyone rosters list with pagination"""
    model = Roster
    paginator_class = Paginator
    paginate_by = settings.OBJECTS_ON_PAGE
    template_name = 'tabletop/roster_list.html'


class UserRosterListView(RostersListView):
    """ Users rosters list with pagination """
    def get_queryset(self):
        return super(UserRosterListView, self).get_queryset().filter(
            owner=self.request.user
        )


class RosterDetailView(generic.DetailView):
    """ Single Roster show"""
    model = Roster
    template_name = 'tabletop/roster.html'

    def get_context_data(self, **kwargs):
        context = super(RosterDetailView, self).get_context_data(**kwargs)
        comments = get_comments(self.model, object_pk=self.kwargs.get('pk', 0))
        comments = paginate(
            comments, self.request.GET.get('page', 1),
            pages=settings.OBJECTS_ON_PAGE
        )
        context.update({
            'comments': comments
        })
        return context