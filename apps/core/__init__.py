#users permissions
from django.conf import settings 
import re

from django.utils.translation import ugettext_lazy as _
from django.template import add_to_builtins
from django.template.loader import get_template,TemplateDoesNotExist
from datetime import datetime
import os

module_name = _('core')

USERPERMS = (('can_test','Can test functional'),)
IMG_MAP = ('jpeg','jpg', 'gif', 'png' )

def make_links_from_pages(pages, url_scheme=''):
	buffer = list()
	for i in xrange(pages):
		buffer.append(
			{'url': '%s?page=%s' % (url_scheme,i+1),
			'num': i+1}
		)
	return buffer

def benchmark(request):
    if hasattr(request,'_now_'):
        return {
            'timeit': datetime.now()-request._now_
        }
    else:
        return {}
def pages(request):
	page = request.GET.get('page','1')
	if not page.isdigit(): page = 1
	return {
		'page': int(page)
	}
def get_skin_template(user,template):
    if hasattr(user,'username'): #.is_authenticated(): #breaks karma
        if hasattr(user,'skin'):
            if user.skin:
	    	skin_path = "skins/%s" % (user.skin.name.lower())
            	skin_path = os.path.join(skin_path,template)
            	try:
                	t = get_template(skin_path)
               		return skin_path
            	except TemplateDoesNotExist:
                	return template
    return template
    
    
#old realization
"""
def get_skin_template(user, template):
	if not hasattr(user,'user'):
		if hasattr(user,'skin'):
			file = "%s/%s" % (user.skin.name.lower(), template)
			import os
			for t in settings.TEMPLATE_DIRS:
				if os.access("%s/skins/%s" % (t,file), os.R_OK):
					#print file
					return 'skins/%s/%s' % ( user.skin.name.lower(), template)
			#print "%s/skins/%s" % (t,file)
			#print template
			return template
		else:
			#print "2 %s" % template
			return template
	else:
		#print "3 %s " % template
		return template
"""

def get_safe_message(message):
	for line in re.findall("<a.[\w\S]*?.*?href=.javascript[\w\S]*?\>*?</a>", message):
		message = message.replace(line,'')
	return message

add_to_builtins('apps.core.templatetags.kamwhfilters')
add_to_builtins('apps.core.templatetags.coretags')
