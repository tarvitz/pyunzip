# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ModelUnit.min'
        db.add_column('tabletop_modelunit', 'min', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)

        # Adding field 'ModelUnit.max'
        db.add_column('tabletop_modelunit', 'max', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ModelUnit.min'
        db.delete_column('tabletop_modelunit', 'min')

        # Deleting field 'ModelUnit.max'
        db.delete_column('tabletop_modelunit', 'max')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 29, 12, 12, 2, 102053)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 29, 12, 12, 2, 101812)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': 'None', 'unique': 'True', 'max_length': '30'}),
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
        'tabletop.army': {
            'Meta': {'object_name': 'Army'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'tabletop.autoroster': {
            'Meta': {'object_name': 'AutoRoster'},
            'army': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auto_rosters'", 'to': "orm['tabletop.Army']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auto_roster_user_set'", 'to': "orm['auth.User']"}),
            'pts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'tabletop.battlereport': {
            'Meta': {'ordering': "['-id']", 'object_name': 'BattleReport'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '10240'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'layout': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'mission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tabletop.Mission']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Owner'", 'to': "orm['auth.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tabletop.Roster']", 'symmetrical': 'False'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner'", 'null': 'True', 'to': "orm['tabletop.Roster']"})
        },
        'tabletop.codex': {
            'Meta': {'object_name': 'Codex'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ct_set_for_codex'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'plain_side': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'revisions': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'tabletop.game': {
            'Meta': {'object_name': 'Game'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'tabletop.mission': {
            'Meta': {'object_name': 'Mission'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tabletop.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'tabletop.modelunit': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'ModelUnit'},
            'army': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'model_units'", 'to': "orm['tabletop.Army']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'min': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'pts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'hq'", 'max_length': '16'})
        },
        'tabletop.roster': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Roster'},
            'codex': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['tabletop.Codex']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'max_length': '10240', 'null': 'True', 'blank': 'True'}),
            'custom_codex': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_orphan': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roster_owner'", 'to': "orm['auth.User']"}),
            'player': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'pts': ('django.db.models.fields.IntegerField', [], {}),
            'revision': ('django.db.models.fields.IntegerField', [], {}),
            'roster': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'tabletop.unitcontainer': {
            'Meta': {'object_name': 'UnitContainer'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': "orm['tabletop.ModelUnit']"}),
            'pts': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'roster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'unit_containers'", 'to': "orm['tabletop.AutoRoster']"})
        },
        'tabletop.wargear': {
            'Meta': {'object_name': 'Wargear'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'model_unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wargear'", 'to': "orm['tabletop.ModelUnit']"}),
            'pts': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'tabletop.wargearcontainer': {
            'Meta': {'object_name': 'WargearContainer'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wargear_containers'", 'to': "orm['tabletop.Wargear']"}),
            'pts': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wargear_containers'", 'to': "orm['tabletop.UnitContainer']"})
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

    complete_apps = ['tabletop']
