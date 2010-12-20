# coding: utf-8
import os,sys

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)

def rel_path(subdir):
    return os.path.join(PROJECT_ROOT, subdir)

MEDIA_ROOT=rel_path('media')
STYLES_ROOT = rel_path('styles')
ADMIN_MEDIA = rel_path('admin_media')
