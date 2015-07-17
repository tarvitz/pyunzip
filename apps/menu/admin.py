# -*- coding: utf-8 -*-

from django.contrib import admin
from apps.menu.models import VMenuItem, HMenuItem
from django.utils.translation import ugettext_lazy as _


class HMenuItemAdmin(admin.ModelAdmin):
    search_fields = ('title', 'order', 'url', 'attrs', )
    list_display = ('get_url', 'title', 'order', 'url', 'attrs', )
    list_editable = ('title', 'order', 'url', 'attrs', )

    def get_url(self, obj):
        return obj.get_url()
    get_url.short_description = _('url')


class VMenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_url', 'is_url', 'path')
    list_editable = ('is_url', )
    search_fields = ('get_title', 'order', 'url', )

    def path(self, obj):
        return obj.__unicode__()
    path.short_description = _("path")

    def get_url(self, obj):
        return obj.get_url()
    get_url.short_description = _("url")

admin.site.register(HMenuItem, HMenuItemAdmin)
admin.site.register(VMenuItem, VMenuItemAdmin)
