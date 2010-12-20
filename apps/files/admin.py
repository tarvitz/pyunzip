from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.files.models import Replay,Game,Version,Gallery,Image,Attachment,File

class GameAdmin(admin.ModelAdmin):
    pass
admin.site.register(Game, GameAdmin)

class VersionAdmin(admin.ModelAdmin):
    list_display = ['game','name','patch',]
    search_fields = ['name','patch','game__name','game__short_name']
    list_display_links = ['name','game']
    list_per_page = 40
    list_filter = ['game','name']

admin.site.register(Version, VersionAdmin)

class ReplayAdmin(admin.ModelAdmin):
    list_display = ('name','type','show_author', 'is_set')
    search_fields = ['name', 'type', 'author__nickname','version__game__name','version__game__short_name','version__name',]
    list_per_page = 40
    list_filter = ['type','author','is_set',]
    fieldsets = (
        (_('Base'),
            {
                'fields': (
                    'name','winner',
                    'version','type',
                    'teams','races',
                    'author',
                ),
                'classes': ('null',)
            }
        ),
        (_('Additional'),
            {
                'fields': (
                    'upload_date','is_set','nonstd_layout',
                ),
                'classes': ('collapse',)
            }
        ),
        (_('Stuff'),
            {
                'fields': (
                    'comments','syntax','replay',
                ),
                'classes': ('collapse',)
            }
        ),
    )
admin.site.register(Replay, ReplayAdmin)

class GalleryAdmin(admin.ModelAdmin):
    list_display = ('name','type')
    list_filter = ('type',)
    list_display_links = ['type','name']
    search_fields = ['name','type']
    list_per_page = 40

admin.site.register(Gallery,GalleryAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ( 'gallery', 'title')
admin.site.register(Image, ImageAdmin)

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'attachment')
admin.site.register(Attachment,AttachmentAdmin)

class FileAdmin(admin.ModelAdmin):
    list_display = ('owner','url','description')
    list_display_links = ('owner','url',)
    list_per_page = 40
    search_fields = ('owner__nickname','description','url')
    list_filter = ('owner',)
    fieldsets = (
        (_('Base'),
            {
                'fields': ('description','owner','upload_date'),
                'classes': ('none',),
            }
        ),
        (_('Additional'),
            {
                'fields': ('file','url'),
                'classes': ('collapse',)
            }
        )
    )
admin.site.register(File, FileAdmin)
