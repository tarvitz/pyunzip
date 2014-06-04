# coding: utf-8
from django.contrib import admin
from apps.tabletop.models import (
    Roster, Game, Mission, BattleReport,
)


class BattleReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'layout', 'approved', 'ip_address')
    search_fields = ['approved', 'title', 'winner']
    list_filter = ['approved', 'layout', 'ip_address']


class GameAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name',)


class RosterAdmin(admin.ModelAdmin):
    list_display = ('show_player', 'codex', 'pts')
    list_display_links = ('show_player', 'codex', 'pts')


admin.site.register(Game, GameAdmin)
admin.site.register(Mission)
admin.site.register(BattleReport, BattleReportAdmin)
admin.site.register(Roster, RosterAdmin)
