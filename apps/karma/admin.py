from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.karma.models import Karma ,KarmaStatus

class KarmaAdmin(admin.ModelAdmin):
    list_display = ('user','voter','value','date')
    list_display_links = ['user','value','voter']
    list_per_page = 40
    search_fields = ('user__nickname','value','voter__nickname')
    
admin.site.register(Karma,KarmaAdmin)


class KarmaStatusAdmin(admin.ModelAdmin):
    list_display = ('status','value','is_general','is_humor')
    list_display_links = ('status','value',)
    search_fields = ('status',)
    list_filter = ('value','is_general','is_humor')
    fieldsets = (
        (_('Base'),
            {
                'fields': ('codename','status','value','description','is_general',),
                'classes': ('null',)
            }
        ),
        (_('Side'),
            {
                'fields': ('side',),
                'classes': ('null',),
            }
        ),
        (_('Additional'),
            {
                'fields': ('syntax','is_humor',),
                'classes': ('collapse',)
            }
        ),
    )
admin.site.register(KarmaStatus,KarmaStatusAdmin)

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
