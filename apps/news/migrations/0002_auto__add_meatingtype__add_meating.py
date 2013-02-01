# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MeatingType'
        db.create_table('news_meatingtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('news', ['MeatingType'])
        from apps.news.models import MeatingType
        mt = MeatingType(title=u'Default', codename='default')
        mt.save()

        # Adding model 'Meating'
        db.create_table('news_meating', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['news.MeatingType'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meating_owner_set', to=orm['auth.User'])),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=4096)),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('author_ipv4', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('author_ipv6', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
        ))
        db.send_create_signal('news', ['Meating'])

        # Adding M2M table for field members on 'Meating'
        db.create_table('news_meating_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meating', models.ForeignKey(orm['news.meating'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('news_meating_members', ['meating_id', 'user_id'])


    def backwards(self, orm):
        
        # Deleting model 'MeatingType'
        db.delete_table('news_meatingtype')

        # Deleting model 'Meating'
        db.delete_table('news_meating')

        # Removing M2M table for field members on 'Meating'
        db.delete_table('news_meating_members')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'army': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.Army']", 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'plain_avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'ranks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['wh.Rank']", 'null': 'True', 'blank': 'True'}),
            'settings': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.Skin']", 'null': 'True', 'blank': 'True'}),
            'tz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'uin': ('django.db.models.fields.IntegerField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        'news.meating': {
            'Meta': {'object_name': 'Meating'},
            'author_ipv4': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'author_ipv6': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meating_user_sets'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meating_owner_set'", 'to': "orm['auth.User']"}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['news.MeatingType']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'news.meatingtype': {
            'Meta': {'object_name': 'MeatingType'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
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
        },
        'wh.army': {
            'Meta': {'ordering': "['side']", 'object_name': 'Army'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'side': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.Side']"})
        },
        'wh.fraction': {
            'Meta': {'object_name': 'Fraction'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'universe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.Universe']", 'null': 'True', 'blank': 'True'})
        },
        'wh.rank': {
            'Meta': {'object_name': 'Rank'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'magnitude': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'side': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['wh.Side']", 'symmetrical': 'False', 'blank': 'True'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.RankType']", 'null': 'True', 'blank': 'True'})
        },
        'wh.ranktype': {
            'Meta': {'object_name': 'RankType'},
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'css_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'magnitude': ('django.db.models.fields.IntegerField', [], {}),
            'style': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'wh.side': {
            'Meta': {'object_name': 'Side'},
            'fraction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wh.Fraction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'wh.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'fraction': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['wh.Fraction']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'wh.universe': {
            'Meta': {'object_name': 'Universe'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['news']
