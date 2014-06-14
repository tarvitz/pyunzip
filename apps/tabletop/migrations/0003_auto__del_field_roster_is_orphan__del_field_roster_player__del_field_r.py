# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Roster.is_orphan'
        db.delete_column(u'tabletop_roster', 'is_orphan')

        # Deleting field 'Roster.player'
        db.delete_column(u'tabletop_roster', 'player')

        # Deleting field 'Roster.user'
        db.delete_column(u'tabletop_roster', 'user_id')

        # Deleting field 'Roster.custom_codex'
        db.delete_column(u'tabletop_roster', 'custom_codex')

        # Adding field 'Roster.roster_cache'
        db.add_column(u'tabletop_roster', 'roster_cache',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Roster.is_orphan'
        db.add_column(u'tabletop_roster', 'is_orphan',
                      self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Roster.player'
        db.add_column(u'tabletop_roster', 'player',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'Roster.user'
        db.add_column(u'tabletop_roster', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='roster_user_set', null=True, to=orm['accounts.User'], blank=True),
                      keep_default=False)

        # Adding field 'Roster.custom_codex'
        db.add_column(u'tabletop_roster', 'custom_codex',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Roster.roster_cache'
        db.delete_column(u'tabletop_roster', 'roster_cache')


    models = {
        u'accounts.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'army': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wh.Army']", 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jid': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'plain_avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'ranks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['wh.Rank']", 'null': 'True', 'blank': 'True'}),
            'settings': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'}),
            'tz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'uin': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tabletop.battlereport': {
            'Meta': {'ordering': "['-id']", 'object_name': 'BattleReport'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '10240'}),
            'deployment': ('django.db.models.fields.CharField', [], {'default': "'dow'", 'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'layout': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tabletop.Mission']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'battle_report_set'", 'to': u"orm['accounts.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rosters': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tabletop.Roster']", 'symmetrical': 'False'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'winners': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'breport_winners_sets'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['tabletop.Roster']"})
        },
        u'tabletop.codex': {
            'Meta': {'object_name': 'Codex'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ct_set_for_codex'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'plain_side': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'revisions': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'tabletop.game': {
            'Meta': {'object_name': 'Game'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        u'tabletop.mission': {
            'Meta': {'object_name': 'Mission'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tabletop.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'tabletop.roster': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Roster'},
            'codex': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['tabletop.Codex']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'max_length': '10240', 'null': 'True', 'blank': 'True'}),
            'defeats': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roster_owner'", 'to': u"orm['accounts.User']"}),
            'pts': ('django.db.models.fields.IntegerField', [], {}),
            'revision': ('django.db.models.fields.IntegerField', [], {}),
            'roster': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'roster_cache': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'wins': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
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
        u'wh.universe': {
            'Meta': {'object_name': 'Universe'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tabletop']