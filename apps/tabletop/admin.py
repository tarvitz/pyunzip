# coding: utf-8
from django.contrib import admin
from apps.tabletop.models import (
    Roster, Game, Mission, Report,
)


class BattleReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'layout', 'is_approved', 'ip_address')
    search_fields = ['title', 'winner']
    list_filter = ['layout', 'is_approved']


class GameAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name',)


class RosterAdmin(admin.ModelAdmin):
    list_display = ('show_player', 'codex', 'pts')
    list_display_links = ('show_player', 'codex', 'pts')


admin.site.register(Game, GameAdmin)
admin.site.register(Mission)
admin.site.register(Roster, RosterAdmin)
