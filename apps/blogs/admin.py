from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.blogs.models import Post,ArchivedPost

class PostAdmin(admin.ModelAdmin):
	list_display = ('date','title', 'author', 'local_content','approved','author_ip','attachment')
	search_fields = [ 'approved','title', 'author', 'head_content','content']
	list_filter = ['approved', 'author', 'author_ip' ]
	
	def local_content(self,obj):
		if obj.head_content:
			return obj.content[0:70] + " ..."
	local_content.short_description = _('content')

admin.site.register(Post,PostAdmin)
admin.site.register(ArchivedPost)

