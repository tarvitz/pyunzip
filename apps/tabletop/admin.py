from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.tabletop.models import (
    Roster, Game, Mission, BattleReport, Codex,
    AutoRoster, ModelUnit, Wargear, UnitContainer, WargearContainer,
    Army, MWRUnit, WargearRequirement, UnitWargearRequirement
)
from apps.tabletop.adminforms import (
    AddWargearContainerForm, WargearContainerForm,
    UnitContainerForm,
    UnitWargearContainerFormset,
    InlineMWRUnitForm
)

class InlineUnitContainer(admin.StackedInline):
    model = UnitContainer
    extra = 0
    readonly_fields = ('pts', 'model_unit', 'amount', )

class InlineMWRUnit(admin.StackedInline):
    model = MWRUnit
    form = InlineMWRUnitForm
    fk_name = 'model_unit'
    extra = 0

class InlineWargearRequirement(admin.StackedInline):
    model = WargearRequirement
    fk_name = 'target'
    extra = 0

class InlineUnitWargearRequirement(admin.StackedInline):
    model = UnitWargearRequirement
    extra = 0

class InlineWargearContainer(admin.StackedInline):
    model = WargearContainer
    form = WargearContainerForm
    formset = UnitWargearContainerFormset
    readonly_fields = ('pts', )
    #fk_name = 'link'
    extra = 0

class BattleReportAdmin(admin.ModelAdmin):
	list_display = ('title','winner','layout' ,'approved','ip_address')
	search_fields = [ 'approved','title', 'winner']
	list_filter = ['approved','layout', 'ip_address' ]
	
    #def mission_content(self,obj):
    #    if hasattr(obj,'mission'):
    #        return obj.mission.title
    #mission_content.short_description = _('mission content')

admin.site.register(BattleReport,BattleReportAdmin)
class GameAdmin(admin.ModelAdmin):
    list_display = ('codename','name',)

admin.site.register(Game,GameAdmin)
admin.site.register(Mission)

class RosterAdmin(admin.ModelAdmin):
    list_display = ('show_player','codex','pts')
    list_display_links = ('show_player','codex','pts')
admin.site.register(Roster,RosterAdmin)

class ModelUnitAdmin(admin.ModelAdmin):
    inlines = [InlineMWRUnit, ]
    list_display = (
        'title', 'type', 'unit_type', 'pts', 'army',
        'is_unique', 'min', 'max'
    )
    list_editable = (
        'type', 'unit_type', 'pts', 'army', 'is_unique',
        'min', 'max'
    )
    list_filter = ('army', 'is_unique')

class WargearAdmin(admin.ModelAdmin):
    inlines = [
        InlineWargearRequirement, InlineUnitWargearRequirement
    ]
    list_display = (
        'show_unit_titles', 'title', 'pts', 'limit', 'threshold',
        'is_squad_only', 'show_blocks', 'show_depends', 'show_combines',
    )
    list_editable = ('title', 'pts', 'is_squad_only', 'limit')
    list_filter = ('model_units', )
    #raw_id_fields = (
    #    #'related_fk',
    #    'blocks',
    #)
    related_lookup_fields = {
        'm2m': ['blocks', ],
    }
    filter_horizontal = ('model_units', 'blocks', 'combines')

    def show_blocks(self, obj):
        titles = ', '.join([
            i['short_title'] for i in obj.blocks.values('short_title')
        ])
        return titles
    show_blocks.short_description = _("blocks")

    def show_depends(self, obj):
        titles = ", ".join([
            i['require__short_title'] for i in obj.wargear_requirements.values('require__short_title')
        ])
        return titles
    show_depends.short_description = _("depends")

    def show_combines(self, obj):
        titles = ", ".join([
            i['short_title'] for i in obj.combines.values('short_title')
        ])
        return titles
    show_combines.short_description = _("combines")

    def show_unit_titles(self, obj):
        units = ", ".join(
            [i['title'] for i in obj.model_units.values('title')]
        )
        race = obj.model_units.all()[0].army.title if obj.model_units.all() else ''
        titles = "%s: %s" % (race, units if len(units) < 40 else units[:40] + "..")
        return titles
    show_unit_titles.short_description = _("Units")

def rebuild_pts(modeladmin, request, queryset):
    for q in queryset:
        q.reload_pts(rebuild=True, recursive=True)
    return queryset
rebuild_pts.short_description = _("Rebuild points")

class AutoRosterAdmin(admin.ModelAdmin):
    inlines = [InlineUnitContainer, ]
    list_display = ('title', 'owner', 'pts')
    readonly_fields = ('pts', )
    actions = [rebuild_pts, ]

class WargearContainerAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'link', 'amount', 'pts')
    form = AddWargearContainerForm
    readonly_fields = ('pts', )

class UnitContainerAdmin(admin.ModelAdmin):
    inlines = [InlineWargearContainer, ]
    form = UnitContainerForm
    list_display = ('__unicode__', 'amount', 'model_unit', 'pts')
    readonly_fields = ('pts', )

class MWRUnitAdmin(admin.ModelAdmin):
    list_display = ('model_unit', 'wargear', )

class WargearRequirementAdmin(admin.ModelAdmin):
    list_display = ('target', 'require', 'amount_target', 'amount')
    list_editable = ('amount_target', 'amount')

class UnitWargearRequirementAdmin(admin.ModelAdmin):
    list_display = ('target', 'require', 'amount_target', 'amount')
    list_editable = ('amount_target', 'amount')

#class CategoryAdmin(admin.ModelAdmin):
#	list_display= ('id','name')
#admin.site.register(Category,CategoryAdmin)
admin.site.register(AutoRoster, AutoRosterAdmin)
admin.site.register(ModelUnit, ModelUnitAdmin)
admin.site.register(Wargear, WargearAdmin)
admin.site.register(UnitContainer, UnitContainerAdmin)
admin.site.register(WargearContainer, WargearContainerAdmin)
admin.site.register(Army)
admin.site.register(MWRUnit, MWRUnitAdmin)
admin.site.register(WargearRequirement, WargearRequirementAdmin)
admin.site.register(UnitWargearRequirement, UnitWargearRequirementAdmin)
