from django.contrib import admin
from apps.tagging.models import Tag, TaggedItem
from apps.tagging.forms import TagAdminForm

class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm

admin.site.register(TaggedItem)
admin.site.register(Tag, TagAdmin)




