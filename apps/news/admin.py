from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.news.models import News,ArchivedNews,Category

class NewsAdmin(admin.ModelAdmin):
    list_display = ('date','category','title', 'author', 'local_content','approved','author_ip','attachment')
    search_fields = [ 'approved','title', 'author', 'head_content','content']
    list_filter = ['approved','category', 'author', 'author_ip' ]
    
    fieldsets = (
        (_('Base'),
            {
                'fields':(
                    'title','author',
                    'editor','head_content',
                    'content','date',
                    'author_ip','category',
                    'url','approved',
                ),
                'classes':('none',),
            }
        ),
        (_("Stuff"),
            {
                'fields':('attachment','syntax','is_event',),
                'classes':('collapse',)
            }
        )
    )
    def local_content(self,obj):
        if obj.head_content:
            return obj.head_content+obj.content[0:70] + " ..."
    local_content.short_description = _('content')

admin.site.register(News,NewsAdmin)
admin.site.register(ArchivedNews)

class CategoryAdmin(admin.ModelAdmin):
    list_display= ('name',)
    search_fields = ('name',)
    list_per_page = 40

admin.site.register(Category,CategoryAdmin)
