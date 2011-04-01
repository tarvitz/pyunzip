# coding: utf-8
from django.core.files.uploadhandler import FileUploadHandler
from django.contrib.sessions.backends.db import SessionStore
from time import sleep

class UploadProgressHandler(FileUploadHandler):
    """Handler which provides progress within file upload"""
    def __init__(self,request,progress_id=None):
        #print "progress handler initialized"
        super(UploadProgressHandler,self).__init__(request)
        self.progress_id = progress_id
        self.cache_key = None
        self.request = request
        #print "session_key: ",self.request.session.session_key
        #print "cache_key: %s\nprogress_id: %s\nrequest: %r" % (self.cache_key,self.progress_id,self.request)

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if self.progress_id:
            self.cache_key = "%s_%s" % (META['REMOTE_ADDR'],self.progress_id)
            try:
                s = SessionStore(session_key=self.request.session.session_key)
                #print "session store: ",s
                #print "session key: ",self.request.session.session_key
            except:
                return None
            s[self.cache_key] = {
                'length': self.content_length,
                'filename': self.file_name,
                'speed': 0,
                'uploaded': 0, #bytes
                'error': u'',
                'progress': 0,
                'complete': False,
            }
            #print s[self.cache_key]
            s.save()
        return None

    def new_file(self,field_name,file_name,content_type,content_length,charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        #print "receive_data_chunk: "
        #print "cache key: ", self.cache_key
        #print "session_key: ", self.request.sesion.session_key
        if self.cache_key:
            try:
                s = SessionStore(session_key=self.request.session.session_key)
            except:
                #print "failed to initialized sessionstore key, returning raw data"
                return raw_data
            data = s[self.cache_key]
            if data:
                #print "saving progress"
                sleep(0.35)
                data['uploaded'] += self.chunk_size 
                if data['uploaded'] > data['length']:
                    data['uploaded'] = data['length'] #SAD BUT TRUE :(
                data['progress'] = round(float(data['uploaded'])/float(data['length'])*100)
                #print "uploaded: ", data['uploaded']
                s[self.cache_key] = data
                s.save()
        #print "returning raw_data"
        return raw_data
    
    def file_complete(self, file_size):
        pass
    
    def upload_complete(self):
        #print "upload_complete"
        if self.cache_key:
            s = SessionStore(session_key=self.request.session.session_key)
            data = s[self.cache_key]
            #print "data: ", data
            if data:
                data['complete'] = True
                #print "if data?: ", data
                s[self.cache_key] = data
                s.save()
                #print "marking upload complete"

