from django.contrib import admin
from apps.karma.models import Karma


class KarmaAdmin(admin.ModelAdmin):
    list_display = ('user', 'voter', 'value', 'date')
    list_display_links = ['user', 'value', 'voter']
    list_per_page = 40
    search_fields = ('user__nickname', 'value', 'voter__nickname')

admin.site.register(Karma, KarmaAdmin)
