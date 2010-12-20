from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from apps.tabletop.models import Roster,Game,Mission,BattleReport

class BattleReportAdmin(admin.ModelAdmin):
	list_display = ('title','winner','layout' ,'approved','ip_address')
	search_fields = [ 'approved','title', 'winner']
	list_filter = ['approved','layout', 'ip_address' ]
	
    #def mission_content(self,obj):
    #    if hasattr(obj,'mission'):
    #        return obj.mission.title
    #mission_content.short_description = _('mission content')

admin.site.register(BattleReport,BattleReportAdmin)
class GameAdmin(admin.ModelAdmin):
    list_display = ('codename','name',)

admin.site.register(Game,GameAdmin)
admin.site.register(Mission)

class RosterAdmin(admin.ModelAdmin):
    list_display = ('show_player','show_race','pts')
    list_display_links = ('show_player','show_race','pts')
admin.site.register(Roster,RosterAdmin)

#class CategoryAdmin(admin.ModelAdmin):
#	list_display= ('id','name')
#admin.site.register(Category,CategoryAdmin)
