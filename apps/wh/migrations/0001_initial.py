# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Universe'
        db.create_table(u'wh_universe', (
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'wh', ['Universe'])

        # Adding model 'Fraction'
        db.create_table(u'wh_fraction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('universe', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.Universe'], null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['Fraction'])

        # Adding model 'Side'
        db.create_table(u'wh_side', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('fraction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.Fraction'])),
        ))
        db.send_create_signal(u'wh', ['Side'])

        # Adding model 'Army'
        db.create_table(u'wh_army', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('side', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.Side'])),
        ))
        db.send_create_signal(u'wh', ['Army'])

        # Adding model 'MiniQuote'
        db.create_table(u'wh_miniquote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'wh', ['MiniQuote'])

        # Adding model 'Expression'
        db.create_table(u'wh_expression', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('original_content', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('fraction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.Fraction'])),
        ))
        db.send_create_signal(u'wh', ['Expression'])

        # Adding model 'Profile'
        db.create_table(u'wh_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('army', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.Army'])),
            ('gender', self.gf('django.db.models.fields.CharField')(default='n', max_length=1, blank=True)),
            ('jid', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uin', self.gf('django.db.models.fields.IntegerField')(max_length=12, blank=True)),
        ))
        db.send_create_signal(u'wh', ['Profile'])

        # Adding model 'PM'
        db.create_table(u'wh_pm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender', to=orm['auth.User'])),
            ('addressee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addressee', to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('is_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')()),
            ('dbs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dba', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['PM'])

        # Adding model 'RegisterSid'
        db.create_table(u'wh_registersid', (
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('expired', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'wh', ['RegisterSid'])

        # Adding model 'WishList'
        db.create_table(u'wh_wishlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('anonymous', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.TextField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=16, null=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wh', ['WishList'])

        # Adding model 'Skin'
        db.create_table(u'wh_skin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('is_general', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wh', ['Skin'])

        # Adding M2M table for field fraction on 'Skin'
        db.create_table(u'wh_skin_fraction', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('skin', models.ForeignKey(orm[u'wh.skin'], null=False)),
            ('fraction', models.ForeignKey(orm[u'wh.fraction'], null=False))
        ))
        db.create_unique(u'wh_skin_fraction', ['skin_id', 'fraction_id'])

        # Adding model 'RankType'
        db.create_table(u'wh_ranktype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('magnitude', self.gf('django.db.models.fields.IntegerField')()),
            ('style', self.gf('django.db.models.fields.TextField')(max_length=1024, null=True, blank=True)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('css_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['RankType'])

        # Adding model 'Rank'
        db.create_table(u'wh_rank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.RankType'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('magnitude', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_general', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['Rank'])

        # Adding M2M table for field side on 'Rank'
        db.create_table(u'wh_rank_side', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rank', models.ForeignKey(orm[u'wh.rank'], null=False)),
            ('side', models.ForeignKey(orm[u'wh.side'], null=False))
        ))
        db.create_unique(u'wh_rank_side', ['rank_id', 'side_id'])

        # Adding model 'UserActivity'
        db.create_table(u'wh_useractivity', (
            ('activity_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('activity_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('is_logout', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('last_action_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['UserActivity'])

        # Adding model 'GuestActivity'
        db.create_table(u'wh_guestactivity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('activity_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('activity_date_prev', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'wh', ['GuestActivity'])

        # Adding model 'WarningType'
        db.create_table(u'wh_warningtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('is_general', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'wh', ['WarningType'])

        # Adding M2M table for field side on 'WarningType'
        db.create_table(u'wh_warningtype_side', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('warningtype', models.ForeignKey(orm[u'wh.warningtype'], null=False)),
            ('side', models.ForeignKey(orm[u'wh.side'], null=False))
        ))
        db.create_unique(u'wh_warningtype_side', ['warningtype_id', 'side_id'])

        # Adding model 'Warning'
        db.create_table(u'wh_warning', (
            ('style', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wh.WarningType'])),
            ('level', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], primary_key=True)),
            ('expired', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'wh', ['Warning'])


    def backwards(self, orm):
        # Deleting model 'Universe'
        db.delete_table(u'wh_universe')

        # Deleting model 'Fraction'
        db.delete_table(u'wh_fraction')

        # Deleting model 'Side'
        db.delete_table(u'wh_side')

        # Deleting model 'Army'
        db.delete_table(u'wh_army')

        # Deleting model 'MiniQuote'
        db.delete_table(u'wh_miniquote')

        # Deleting model 'Expression'
        db.delete_table(u'wh_expression')

        # Deleting model 'Profile'
        db.delete_table(u'wh_profile')

        # Deleting model 'PM'
        db.delete_table(u'wh_pm')

        # Deleting model 'RegisterSid'
        db.delete_table(u'wh_registersid')

        # Deleting model 'WishList'
        db.delete_table(u'wh_wishlist')

        # Deleting model 'Skin'
        db.delete_table(u'wh_skin')

        # Removing M2M table for field fraction on 'Skin'
        db.delete_table('wh_skin_fraction')

        # Deleting model 'RankType'
        db.delete_table(u'wh_ranktype')

        # Deleting model 'Rank'
        db.delete_table(u'wh_rank')

        # Removing M2M table for field side on 'Rank'
        db.delete_table('wh_rank_side')

        # Deleting model 'UserActivity'
        db.delete_table(u'wh_useractivity')

        # Deleting model 'GuestActivity'
        db.delete_table(u'wh_guestactivity')

        # Deleting model 'WarningType'
        db.delete_table(u'wh_warningtype')

        # Removing M2M table for field side on 'WarningType'
        db.delete_table('wh_warningtype_side')

        # Deleting model 'Warning'
        db.delete_table(u'wh_warning')


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
        u'comments.comment': {
            'Meta': {'ordering': "('submit_date',)", 'object_name': 'Comment', 'db_table': "'django_comments'"},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comment_comments'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'wh.army': {
            'Meta': {'ordering': "['side']", 'object_name': 'Army'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'side': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Side']"})
        },
        u'wh.expression': {
            'Meta': {'ordering': "['id']", 'object_name': 'Expression'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'fraction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Fraction']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_content': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'wh.fraction': {
            'Meta': {'object_name': 'Fraction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'universe': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Universe']", 'null': 'True', 'blank': 'True'})
        },
        u'wh.guestactivity': {
            'Meta': {'object_name': 'GuestActivity'},
            'activity_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'activity_date_prev': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'activity_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wh.miniquote': {
            'Meta': {'object_name': 'MiniQuote'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'wh.pm': {
            'Meta': {'object_name': 'PM'},
            'addressee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addressee'", 'to': u"orm['auth.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'dba': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dbs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender'", 'to': u"orm['auth.User']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'wh.profile': {
            'Meta': {'object_name': 'Profile'},
            'army': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Army']"}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'uin': ('django.db.models.fields.IntegerField', [], {'max_length': '12', 'blank': 'True'})
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
        u'wh.registersid': {
            'Meta': {'object_name': 'RegisterSid'},
            'expired': ('django.db.models.fields.DateTimeField', [], {}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
        },
        u'wh.useractivity': {
            'Meta': {'object_name': 'UserActivity'},
            'activity_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'activity_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'is_logout': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'last_action_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'wh.warning': {
            'Meta': {'object_name': 'Warning'},
            'expired': ('django.db.models.fields.DateTimeField', [], {}),
            'level': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.WarningType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'primary_key': 'True'})
        },
        u'wh.warningtype': {
            'Meta': {'object_name': 'WarningType'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'side': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['wh.Side']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'wh.wishlist': {
            'Meta': {'object_name': 'WishList'},
            'anonymous': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True'}),
            'post': ('django.db.models.fields.TextField', [], {}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['wh']