from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.vote.models import Vote,Rate


class RateAdmin(admin.ModelAdmin):
    list_display = ('rate','object_pk','content_type')
    list_display_links = ('rate','object_pk','content_type')
    search_fields = ('rate','object_pk')

admin.site.register(Rate,RateAdmin)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('votes','score',)
    fieldsets = (
        (_('Base'),
            {
                'fields':('votes','score')
            }
        ),
        (_('Users'),
            {
                'classes': ('collapse',),
                'fields':('users',)
            }
        ),
    )
    list_filter = ['users',]
    list_display_links = ['votes','score']
    search_fields = ['votes','score']
    list_per_page = 40

admin.site.register(Vote,VoteAdmin)

"""
class NewsAdmin(admin.ModelAdmin):
    list_display = ('date','category','title', 'author', 'local_content','approved','author_ip','attachment')
    search_fields = [ 'approved','title', 'author', 'head_content','content']
    list_filter = ['approved','category', 'author', 'author_ip' ]
    
    def local_content(self,obj):
        if obj.head_content:
            return obj.head_content+obj.content[0:70] + " ..."
    local_content.short_description = _('content')

admin.site.register(News,NewsAdmin)
class CategoryAdmin(admin.ModelAdmin):
    list_display= ('id','name')
admin.site.register(Category,CategoryAdmin)
"""
