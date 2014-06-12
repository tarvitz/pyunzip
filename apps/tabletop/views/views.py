# coding: utf-8
from apps.tabletop.models import (
    Roster, BattleReport, Codex
)
from apps.tabletop.forms import (
    AddBattleReportForm, AddBattleReportModelForm, AddCodexModelForm,
    AddRosterModelForm, RosterForm)

from django.core.urlresolvers import reverse, reverse_lazy
from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.core.helpers import (
    get_comments, get_content_type,
    get_object_or_None, paginate, render_to, get_int_or_zero
)

from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.core import get_skin_template

from apps.core.shortcuts import direct_to_template
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import get_user_model

from django.http import (
    HttpResponse, HttpResponseRedirect,
    Http404
)
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from apps.core.decorators import (
    has_permission
)

from django.views.decorators.csrf import csrf_protect
from django.contrib.comments.models import Comment
from django.views import generic

import simplejson as json
from django.core.cache import cache

from datetime import datetime


User = get_user_model()

@login_required
@render_to('tabletop/reports.html')
def reports(request):
    battle_reps = request.user.battle_report_set.all()
    page = get_int_or_zero(request.GET.get('page')) or 1
    battle_reps = paginate(battle_reps, page, pages=settings.OBJECTS_ON_PAGE)
    form = AddBattleReportForm()
    return {
        'reports': battle_reps,
        'form': form
    }


@render_to('tabletop/reports/reports.html')
def battle_reports(request):
    page = get_int_or_zero(request.GET.get('page', 1)) or 1
    can_edit = request.user.has_perm('tabletop.edit_battle_report')
    kw = {}
    if not can_edit:
        kw.update({'approved': True})
    battle_reps = paginate(
        BattleReport.objects.filter(**kw), page,
        pages=settings.OBJECTS_ON_PAGE
    )
    return {
        'reports': battle_reps
    }


@render_to('tabletop/reports/report.html')
def report(request, pk):
    can_edit = False
    if request.user.is_authenticated():
        can_edit = request.user.has_perm('tabletop.edit_battle_report')
    kw = {'pk': pk}
    if not can_edit:
        kw.update({'approved': True})
    battle_rep = cache.get('tabletop:report:%s' % pk)
    if not battle_rep:
        battle_rep = get_object_or_404(BattleReport, **kw)
        cache.set('tabletop:report:%s' % battle_rep.pk, battle_rep)
    else:
        if not can_edit and not battle_rep.approved:
            raise Http404("Not allowed")

    ct = ContentType.objects.get(
        app_label=battle_rep._meta.app_label,
        model=battle_rep._meta.model_name
    )
    comments = Comment.objects.filter(content_type=ct,
                                      object_pk=str(battle_rep.pk))
    comments_on_page = settings.OBJECTS_ON_PAGE
    page = get_int_or_zero(request.GET.get('page', 1)) or 1

    comments = paginate(
        comments, page,
        pages=comments_on_page
    )
    return {'report': battle_rep, 'comments': comments}


@login_required
@render_to('tabletop/reports/report.html')
def report_approve(request, pk, approved=True):
    can_edit = request.user.has_perm('tabletop.edit_battle_report')
    if not can_edit:
        raise Http404("hands off")
    battle_rep = get_object_or_404(BattleReport, pk=pk)
    battle_rep.approved = approved
    battle_rep.save()
    return {
        'redirect': 'tabletop:report',
        'redirect-args': (battle_rep.id, )
    }


@login_required
def unorphan(request, pk):
    roster = get_object_or_None(Roster, pk=pk)
    if roster:
        roster.is_orphan = False
        roster.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@render_to('tabletop/add_roster.html', allow_xhr=True)
def action_roster(request, pk=None, action=None):
    instance = None
    if pk:
        instance = get_object_or_404(Roster, pk=pk)

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


#@todo: may be should be MORE CLEAN?
@login_required
def add_battle_report(request, action=None, pk=None):
    template = get_skin_template(request.user, 'add_battle_report.html')
    br = None
    if action == 'edit':
        br = get_object_or_404(BattleReport, pk=pk)
    if request.method == 'POST':
        form = AddBattleReportModelForm(request.POST, request=request,
                                        instance=br)
        if form.is_valid():
            instance = form.instance
            instance.owner = request.user
            instance.published = datetime.now()
            instance.approved = True
            instance.ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
            form.save()
            return HttpResponseRedirect(reverse('tabletop:battle-report'))
        else:
            return direct_to_template(request, template, {'form': form})
    form = AddBattleReportModelForm(instance=br)
    return direct_to_template(request, template, {'form': form})


@login_required
@render_to('tabletop/reports.html', allow_xhr=True)
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
    queryset = (
        Q(title__icontains=search)
        | Q(owner__nickname__icontains=search)
        | Q(pts__icontains=search)
        | Q(codex__title__icontains=search)
        | Q(codex__plain_side__icontains=search)
        | Q(custom_codex__icontains=search)
        | Q(player__icontains=search)
    )
    rosters = Roster.objects.filter(queryset)

    raw = [(r.pk, r.__unicode__()) for r in rosters]
    lw_rosters = [{'pk': r[0], 'title': r[1]} for r in raw]

    if lw_rosters > 20:
        lw_rosters = lw_rosters[:20]
    response.write(json.dumps(lw_rosters))
    return response


@login_required
def delete_battle_report(request, pk, approve=''):
    br = get_object_or_None(BattleReport, pk=pk)
    if (br.owner == request.user or request.user.is_superuser
            or request.user.has_perm('tabletop.delete_battlereports')):
        if br:
            br.delete()
            return HttpResponseRedirect(reverse('tabletop:battle-report'))
        else:
            return HttpResponseRedirect('/report/doest/not/exist')
    return HttpResponseRedirect('/permission/denied')


@csrf_protect
@login_required
@has_permission('tabletop.add_codex')
def action_codex(request, pk=None, action=None):
    template = get_skin_template(request.user, 'add_codex.html')
    instance = None
    if pk:
        instance = get_object_or_404(Codex, pk=pk)
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
            return HttpResponseRedirect(reverse('tabletop:codex',
                                                args=(instance.pk,)))
        else:
            return direct_to_template(request, template,
                                      {'form': form})
    form = AddCodexModelForm(instance=instance)
    return direct_to_template(request, template, {'form': form})


@login_required
def show_codex(request, pk):
    template = get_skin_template(request.user, 'show_codex.html')
    codex = get_object_or_404(Codex, id=pk)
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


class RosterAccessMixin(object):
    def get_queryset(self):
            qs = super(RosterAccessMixin, self).get_queryset()
            return qs.filter(owner=self.request.user)


class RosterCreateView(generic.CreateView):
    model = Roster
    template_name = 'tabletop/roster_form.html'
    form_class = RosterForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(RosterCreateView, self).form_valid(form)


class RosterUpdateView(RosterAccessMixin, generic.UpdateView):
    model = Roster
    template_name = 'tabletop/roster_form.html'
    form_class = RosterForm

    def form_valid(self, form):
        return super(RosterUpdateView, self).form_valid(form)


class RosterDeleteView(RosterAccessMixin, generic.DeleteView):
    model = Roster
    template_name = 'tabletop/roster_form.html'
    success_url = reverse_lazy('tabletop:rosters')

    def get_context_data(self, **kwargs):
        context = super(RosterDeleteView, self).get_context_data(**kwargs)
        context.update({
            'delete': True
        })
        return context