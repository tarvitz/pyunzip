from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.core.models import Announcement,Css 

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('content_type','object_pk')
admin.site.register(Announcement, AnnouncementAdmin)

class CssAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user',)
    list_display_links = ('user',)
admin.site.register(Css,CssAdmin)
