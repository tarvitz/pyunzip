
from django.contrib import admin

class GenericAdmin(admin.ModelAdmin):
    class Media:
        js = (
              '/media/tinyfck/tiny_mce.js',
              '/media/textareas.js',
              )
    @staticmethod
    def register(model):
        admin.site.register(model, GenericAdmin)