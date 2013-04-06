# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HMenuItem'
        db.create_table(u'menu_hmenuitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('is_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'menu', ['HMenuItem'])

        # Adding model 'VMenuItem'
        db.create_table(u'menu_vmenuitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['menu.VMenuItem'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('is_url', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'menu', ['VMenuItem'])


    def backwards(self, orm):
        # Deleting model 'HMenuItem'
        db.delete_table(u'menu_hmenuitem')

        # Deleting model 'VMenuItem'
        db.delete_table(u'menu_vmenuitem')


    models = {
        u'menu.hmenuitem': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'HMenuItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'menu.vmenuitem': {
            'Meta': {'ordering': "['is_url', 'order', 'id']", 'object_name': 'VMenuItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_url': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['menu.VMenuItem']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['menu']