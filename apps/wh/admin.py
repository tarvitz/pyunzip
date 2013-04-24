# ^^, coding: utf-8 ^^,

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.wh.models import (
    Expression, Fraction, Side, Army, PM, RegisterSid,
    Skin, Rank,
    RankType, UserActivity,
    GuestActivity, Warning, WarningType,
    Universe
)
from apps.wh.models import MiniQuote


class ExpressionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'show_author', 'show_original_content', 'show_content', 'fraction'
    )
    fieldsets = (
        (
            _('Base'),
            {'fields': ('author', 'fraction')}
        ),
        (
            _('Content'),
            {'fields': ('original_content', 'content')}
        )
    )
    ordering = ('id', )
    search_fields = ['author', 'original_content', 'content']
    #list_filter = ['author']
    list_filter = ['fraction', ]
    list_display_links = ('show_author', 'show_original_content', 'show_content')
    list_per_page = 30
admin.site.register(Expression, ExpressionAdmin)


class FractionAdmin(admin.ModelAdmin):
    list_display = ('title', )
    ordering = ('id', )
admin.site.register(Fraction, FractionAdmin)
admin.site.register(Side)


class ArmyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'side')
    fieldsets = (
        (
            _('Armies'),
            {'fields': ('name', 'side')}
        ),
    )
    list_filter = ['side']
admin.site.register(Army, ArmyAdmin)


class PMAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'is_read', 'dbs', 'dba', 'sent'
    )
admin.site.register(PM, PMAdmin)


class RegisterSidAdmin(admin.ModelAdmin):
    list_display = ('sid', 'ip', 'value', 'expired')
admin.site.register(RegisterSid, RegisterSidAdmin)


class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', )
admin.site.register(Skin, SkinAdmin)


class RankAdmin(admin.ModelAdmin):
    list_display = ('type', 'short_name', 'codename', 'description')
    list_display_links = ('type', 'short_name', 'codename')
    list_filter = ('type', )
    search_fields = ('type', 'short_name', 'codename')
admin.site.register(Rank, RankAdmin)


class RankTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'group', 'magnitude', 'css_id', 'css_class')
    list_display_links = ('type', 'group',)
admin.site.register(RankType, RankTypeAdmin)


class MiniQuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'content')
admin.site.register(MiniQuote, MiniQuoteAdmin)


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('show_nickname', 'activity_date', 'activity_ip')
admin.site.register(UserActivity, UserActivityAdmin)


class GuestActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity_date', 'activity_date_prev', 'activity_ip')
admin.site.register(GuestActivity, GuestActivityAdmin)


class WarningAdmin(admin.ModelAdmin):
    list_display = ('show_nickname', 'level', 'type', 'expired',)
admin.site.register(Warning, WarningAdmin)
admin.site.register(WarningType)


class UniverseAdmin(admin.ModelAdmin):
    list_display = ('codename', 'title')
admin.site.register(Universe, UniverseAdmin)
