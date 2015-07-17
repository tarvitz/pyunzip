# -*- coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from apps.pybb.models import Category, Forum, Topic, AnonymousPost, Post, Read
from django.conf import settings


#: actions
def revert_hidden(modeladmin, request, queryset):
    for q in queryset:
        q.is_hidden = not q.is_hidden
        q.save()
    return queryset


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'forum_count']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['position']
    search_fields = ['name']


class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'position', 'topic_count', 'css_icon',
                    'is_hidden', 'is_private']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-category']
    search_fields = ['name', 'category__name']
    list_editable = ['css_icon', ]
    actions = [revert_hidden, ]
    fieldsets = (
        (
            None, {
                'fields': ('category', 'name', 'css_icon', 'updated',
                           'is_hidden',)
            }
        ),
        (
            _('Additional options'), {
                'classes': ('collapse',),
                'fields': ('position', 'description', 'post_count',
                           'moderators', 'is_private', 'participants')
            }
        ),
    )


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created', 'head', 'post_count']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['name']
    fieldsets = (
        (
            None, {
                'fields': ('forum', 'name', 'user', ('created', 'updated'))
            }
        ),
        (
            _('Additional options'), {
                'classes': ('collapse',),
                'fields': (
                    ('views', 'post_count'), ('sticky', 'closed'),
                    'subscribers'
                )
            }
        ),
    )


class AnonymousPostAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-created']
    search_fields = ['title']


class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created', 'updated', 'summary']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-created']
    date_hierarchy = 'created'
    search_fields = ['body']
    fieldsets = (
        (
            None, {
                'fields': ('topic', 'user', 'markup')
            }
        ),
        (
            _('Additional options'), {
                'classes': ('collapse',),
                'fields': (('created', 'updated'), 'user_ip')
            }
        ),
        (
            _('Message'), {
                'fields': ('body', 'body_html', 'body_text')
            }
        ),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_zone', 'location', 'language']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    fieldsets = (
        (
            None, {
                'fields': ('user', 'time_zone', 'markup', 'location',
                           'language')
            }
        ),
        (
            _('IM'), {
                'classes': ('collapse',),
                'fields': ('jabber', 'icq', 'msn', 'aim', 'yahoo')
            }
        ),
        (
            _('Additional options'), {
                'classes': ('collapse',),
                'fields': ('site', 'avatar', 'signature', 'show_signatures')
            }
        ),
    )


class ReadAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'time']
    list_per_page = settings.OBJECTS_ON_PAGE
    ordering = ['-time']
    date_hierarchy = 'time'
    search_fields = ['user__username', 'topic__name']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(AnonymousPost, AnonymousPostAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Read, ReadAdmin)
