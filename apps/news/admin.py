from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.news.models import (
    EventPlace, Note
)
from apps.news.adminforms import EventPlaceForm


def make_approved_action(modeladmin, request, queryset):
    queryset.update(approved=True)
make_approved_action.short_description = _('Approved news')


def revert_approved(modeladmin, request, queryset):
    for q in queryset:
        q.approved = not q.approved
        q.save()
revert_approved.short_description = _('Revert approved flag')


#AdminModels
class NewsAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'title', 'author', 'approved',
                    'author_ip', 'attachment')
    search_fields = ['approved', 'title', 'author', 'content']
    list_filter = ['approved', 'category', 'author', 'author_ip']
    actions = [make_approved_action, revert_approved]
    fieldsets = (
        (
            _('Base'), {
                'fields': (
                    'owner',
                    'title', 'author',
                    'editor',

                    'content', 'date',
                    'author_ip', 'category',
                    'url', 'approved',),
                'classes': ('none',),
            }
        ),
        (
            _("Stuff"), {
                'fields': ('attachment', 'syntax', 'is_event', ),
                'classes': ('collapse',)}
        )
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)
    list_per_page = 40


class EventPlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'contacts', )
    form = EventPlaceForm


admin.site.register(EventPlace, EventPlaceAdmin)

admin.site.register(Note)

# disabled
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(News, NewsAdmin)
# admin.site.register(ArchivedNews)
