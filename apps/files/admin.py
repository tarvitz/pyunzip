# coding: utf-8
from django.contrib import admin
from apps.files.models import Gallery, Image


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)
    list_display_links = ['type', 'name']
    search_fields = ['name', 'type']
    list_per_page = 40


class ImageAdmin(admin.ModelAdmin):
    list_display = ('gallery', 'title')


admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Image, ImageAdmin)
