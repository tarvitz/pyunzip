# coding: utf-8
import os

from django.utils.translation import ugettext_lazy as _
from os import stat,mkdir
from datetime import datetime
from hashlib import md5
from django.conf import settings
from cStringIO import StringIO
import zipfile
import bz2

def is_zip_file(rawdata):
    file = ''
    for i in rawdata.chunks(): file += i
    try:
        from zipfile import ZipFile,BadZipfile
        zip_file = ZipFile(StringIO(file),mode='r')
        return True
    except BadZipfile:
        return False

def safe_filename(path, filename):
    try:
    #FIXME: perms
        stat(path+'/'+filename)
        now = datetime.now().__format__('%d%m%y-%H_%M_%S-')
        return now+filename
    except OSError: #new file
        return filename

def save_uploaded_file(raw_data,path,compress=False):
    file_name = raw_data.name
    file = ''
    for i in raw_data.chunks(): file += i
    try:
        stat(path)
    except OSError:
        try:
            mkdir('%s' % (path), 0775)
        except OSError as (errno,stderr):
            if errno == 13:
                #perm denied
                raise "Permission denied"
            elif errno == 17:
                pass
            else:
                #TODO: implement some kind of logger here
                pass
            #return None
    file_path = '%s/%s' % (path, file_name)
    try:
    #FIXME: perms
    #TODO: add wise md5 check
        stat(file_path)
        old_file = ''
        now = datetime.now()
        now = str(now)[:10]
        new_md5 = md5(file).hexdigest()
        old_fp = open(file_path,'r')
        for i in old_fp: old_file += i
        old_md5 = md5(old_file).hexdigest()
        if old_md5 == new_md5:
            return 0 #new file = old file
        else:
            file_path = "%s/[%s]%s" % (path, now , file_name)
            if not compress:
                open(file_path, 'wb+').write(file)
                print "compress = False"
            else:
                #zip_buffer = StringIO()
                #zip_instance = zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED)
                #zip_instance.writestr('%s' % file_name,file)
                #zip_buffer.seek(0)
                bz2buff = bz2.compress(file)
                open("%s.bz2" % file_path, 'wb+').write(bz2buff)
                #zip_instance.close()
                #zip_buffer.close()
    except OSError: #new file
        try:
            from os import makedirs
            makedirs(path,0775)
        except:
            pass
        if not compress:
            open(file_path,'wb+').write(file)
        else:
                #zip_buffer = StringIO()
                #zip_instance = zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED)
                #zip_instance.writestr('%s' % file_name,file)
                #zip_buffer.seek(0)
                bz2buff = bz2.compress(file)
                open("%s.bz2" % file_path, 'wb+').write(bz2buff)
                #zip_instance.close()
                #zip_buffer.close()

    file_path = file_path[len(settings.MEDIA_ROOT):]
    if file_path[0] == '/': 
        file_path =  file_path[1:]
        if compress:
            return "%s.bz2" % file_path
    return file_path

def save_thmb_image(path,thmb_path,raw_data,size=(200,200)):
    from PIL import Image
    if path[len(path)-1] == '/': path = path[:-1]
    if thmb_path[len(path)-1] == '/': thmb_path = thmb_path[:-1]
    file = ''
    file_name = raw_data.name
        
    for i in raw_data.chunks(): file += i
    image = Image.open(StringIO(file))
    file_name = safe_filename(path,file_name) #check if file exists, FALSE if duplicate file
    from os import makedirs
    try:
        makedirs(path,0775)
    except: pass
    try: makedirs(thmb_path, 0775)
    except: pass
    #thumbnails makeing
    image.save(path+'/'+file_name)
    db_path = path[len(settings.MEDIA_ROOT):]+'/'+file_name #/var/www/project/media/... - /var/www/project/media 
    if db_path[0] == '/': db_path = db_path[1:]
    x,y = image.size
    size_x,size_y = size
    if (x > size_x or y > size_y):
        y_sz,x_sz = size_x,size_x
        if x>y:    y_sz = int(y*((size_y/(x/100.0))/100.0))
        if y>x: x_sz = int(x*((size_x/(y/100.0))/100.0))
        image=image.resize((x_sz,y_sz))
    image.save(os.path.join(thmb_path,file_name))
    thmb_db_path = thmb_path[len(settings.MEDIA_ROOT):]+'/'+file_name
    if thmb_db_path[0] == '/': thmb_db_path = thmb_db_path[1:]
    return (db_path,thmb_db_path)

#not implemented yet
"""
def save_image(path,raw_data):
    from PIL import Image
    if path[len(path)-1] == '/': path = path[:-1]
    file = ''
    file_name = raw_data.name
    for i in raw_data.chunks(): file += i
    image = Image.open(StringIO(file))
    file_name = md5validate(path,file_name) #check if file exists, FALSE if duplicate file
    if not file_name:
        return False
    try:
        from os import makedirs
        makedirs(path,0775)
    except: 
        pass
    image.save(path+'/'+file_name)
    db_path = path[len(MEDIA_ROOT):]+file_name
    if db_path[0] == '/': db_path = db_path[1:]
    return db_path
"""


class ZipPack():
    def __init__(self,filename=None,buffer=None,mode='rb'):
        if filename:
            self.filename = filename
            try:
                self.file = zipfile.ZipFile(file=self.filename)
            except zipfile.BadZipfile:
                raise "this file does not zip file"
        elif buffer:
            self.filename='_buffered_file'
            self.buffer = buffer
            try:
                self.file = zipfile.ZipFile(file=StringIO(self.buffer))
            except zipfile.BadZipfile:
                raise "this file does not zip file"

    def get_filelist(self):
        return self.file.namelist()

    def unpack(self,folder=''):
        if not folder:
           folder=os.tempnam(os.getcwd(),'dowrep')
        self.folder = folder
        #create folder
        try:
            os.mkdir(folder)
        except OSError as (errno, stderr):
            if errno == 13:
                raise "making temporary folder %s" % stderr
        if os.access(folder,os.W_OK|os.R_OK):
            #unpack here
            try:
                self.file.extractall(pwd=os.getcwd(),path=folder)
            except OSError as (errno,stderr):
                raise "Could not unpack files"
        else:
            #there is no folder or permissions we need =\
            #try to check folder existance
            raise "Could not unpack files, there is no folder [%s] or permissons to read/write" % (folder)
        
    def cleanse(self):
            for root,folders,files in os.walk(self.folder):
                try:
                    if files:
                        for f in files:
                            os.unlink(os.path.join(root,f))
                            #print "root: %s" % root
                    if folders:
                        for f in folders:
                            os.removedirs(os.path.join(root,f))
                except:
                    pass
            try:
                os.removedirs(root)
            except:
                pass

    def get_full_info(self):
        if not hasattr(self,'file'):
            raise "There is not file instance!"
        info = dict()
        info['files'] = self.file.namelist()
        info['info'] = list()
        sub_info = dict()
        map = ['filename','orig_filename','date_time','compress_type','compress_size',
            'file_size','comment']
        for idx in range(0,len(self.file.infolist())):
            for m in map:
                sub_info[m] = getattr(self.file.infolist()[idx],m)
            if sub_info['filename'].endswith('/'):
                sub_info['node_type'] = 'folder'
            else:
                sub_info['node_type'] = 'file'
            small_filename = sub_info['filename'].split('/')
            small_filename = small_filename[len(small_filename)-1]
            sub_info['small_filename'] = small_filename
            sub_info['idx'] = idx
            info['info'].append(sub_info)
            sub_info = dict()

        #unsubscriptable ? O____________O
        #for info in self.file.infolist():
            #map = ['filename','orig_filename','date_time','compress_type','compress_size',
            #    'file_size','comment']
            #for m in map:
            #    sub_info[m] = getattr(info,m)
            #print sub_info
            #info['files_info'].append(sub_info)
        return info
