# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'News.author'
        db.alter_column(u'news_news', 'author', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'News.editor'
        db.alter_column(u'news_news', 'editor', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'ArchivedNews.author'
        db.alter_column(u'news_archivednews', 'author', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'ArchivedNews.editor'
        db.alter_column(u'news_archivednews', 'editor', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'News.author'
        db.alter_column(u'news_news', 'author', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'News.editor'
        db.alter_column(u'news_news', 'editor', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'ArchivedNews.author'
        db.alter_column(u'news_archivednews', 'author', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'ArchivedNews.editor'
        db.alter_column(u'news_archivednews', 'editor', self.gf('django.db.models.fields.CharField')(max_length=30))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'army': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Army']", 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'plain_avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'ranks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['wh.Rank']", 'null': 'True', 'blank': 'True'}),
            'settings': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Skin']", 'null': 'True', 'blank': 'True'}),
            'tz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'uin': ('django.db.models.fields.IntegerField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'files.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'news.archivednews': {
            'Meta': {'object_name': 'ArchivedNews'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attachment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['files.Attachment']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author_ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'cache_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'archivednews'", 'to': u"orm['auth.User']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '32'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'news.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'news.meating': {
            'Meta': {'ordering': "['created_on', '-id']", 'object_name': 'Meating'},
            'author_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'author_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meating_user_sets'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meating_owner_set'", 'to': u"orm['auth.User']"}),
            'syntax': ('django.db.models.fields.CharField', [], {'default': "'textile'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['news.MeatingType']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'news.meatingtype': {
            'Meta': {'object_name': 'MeatingType'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'news.news': {
            'Meta': {'object_name': 'News'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attachment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['files.Attachment']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author_ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'cache_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_event': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'news'", 'to': u"orm['auth.User']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'queued'", 'max_length': '32'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'tracker.seenobject': {
            'Meta': {'object_name': 'SeenObject'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_seenobject'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'wh.army': {
            'Meta': {'ordering': "['side']", 'object_name': 'Army'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'side': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Side']"})
        },
        u'wh.fraction': {
            'Meta': {'object_name': 'Fraction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'universe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Universe']", 'null': 'True', 'blank': 'True'})
        },
        u'wh.rank': {
            'Meta': {'object_name': 'Rank'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'magnitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'side': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['wh.Side']", 'symmetrical': 'False', 'blank': 'True'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.RankType']", 'null': 'True', 'blank': 'True'})
        },
        u'wh.ranktype': {
            'Meta': {'object_name': 'RankType'},
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'css_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'magnitude': ('django.db.models.fields.IntegerField', [], {}),
            'style': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'wh.side': {
            'Meta': {'object_name': 'Side'},
            'fraction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Fraction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'wh.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'fraction': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['wh.Fraction']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'wh.universe': {
            'Meta': {'object_name': 'Universe'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['news']