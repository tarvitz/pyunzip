# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('news_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('news', ['Category'])

        # Adding model 'ArchivedNews'
        db.create_table('news_archivednews', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('editor', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('head_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('author_ip', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['news.Category'])),
            ('is_event', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('attachment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['files.Attachment'], null=True, blank=True)),
        ))
        db.send_create_signal('news', ['ArchivedNews'])

        # Adding model 'News'
        db.create_table('news_news', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('editor', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('head_content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('author_ip', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['news.Category'])),
            ('is_event', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('attachment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['files.Attachment'], null=True, blank=True)),
        ))
        db.send_create_signal('news', ['News'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('news_category')

        # Deleting model 'ArchivedNews'
        db.delete_table('news_archivednews')

        # Deleting model 'News'
        db.delete_table('news_news')


    models = {
        'files.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'news.archivednews': {
            'Meta': {'object_name': 'ArchivedNews'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attachment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['files.Attachment']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'author_ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'head_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'news.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'news.news': {
            'Meta': {'object_name': 'News'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attachment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['files.Attachment']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'author_ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'head_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['news']
