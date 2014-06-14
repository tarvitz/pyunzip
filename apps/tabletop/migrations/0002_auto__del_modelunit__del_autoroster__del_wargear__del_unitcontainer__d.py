# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'MWRUnit', fields ['model_unit', 'wargear']
        db.delete_unique(u'tabletop_mwrunit', ['model_unit_id', 'wargear_id'])

        # Deleting model 'ModelUnit'
        db.delete_table(u'tabletop_modelunit')

        # Deleting model 'AutoRoster'
        db.delete_table(u'tabletop_autoroster')

        # Deleting model 'Wargear'
        db.delete_table(u'tabletop_wargear')

        # Removing M2M table for field blocks on 'Wargear'
        db.delete_table(db.shorten_name(u'tabletop_wargear_blocks'))

        # Removing M2M table for field combines on 'Wargear'
        db.delete_table(db.shorten_name(u'tabletop_wargear_combines'))

        # Removing M2M table for field model_units on 'Wargear'
        db.delete_table(db.shorten_name(u'tabletop_wargear_model_units'))

        # Deleting model 'UnitContainer'
        db.delete_table(u'tabletop_unitcontainer')

        # Deleting model 'WargearContainer'
        db.delete_table(u'tabletop_wargearcontainer')

        # Deleting model 'Army'
        db.delete_table(u'tabletop_army')

        # Deleting model 'UnitWargearRequirement'
        db.delete_table(u'tabletop_unitwargearrequirement')

        # Deleting model 'MWRUnit'
        db.delete_table(u'tabletop_mwrunit')

        # Deleting model 'WargearRequirement'
        db.delete_table(u'tabletop_wargearrequirement')


        # Changing field 'Roster.user'
        db.alter_column(u'tabletop_roster', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['accounts.User']))

        # Changing field 'Roster.owner'
        db.alter_column(u'tabletop_roster', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User']))

        # Changing field 'BattleReport.owner'
        db.alter_column(u'tabletop_battlereport', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User']))

    def backwards(self, orm):
        # Adding model 'ModelUnit'
        db.create_table(u'tabletop_modelunit', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=4096, blank=True)),
            ('max', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('is_dedicated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pts', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('army', self.gf('django.db.models.fields.related.ForeignKey')(related_name='model_units', to=orm['tabletop.Army'])),
            ('min', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('unit_type', self.gf('django.db.models.fields.CharField')(default='infantry', max_length=32)),
            ('is_unique', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.CharField')(default='hq', max_length=16)),
            ('mwr_amount', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tabletop', ['ModelUnit'])

        # Adding model 'AutoRoster'
        db.create_table(u'tabletop_autoroster', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=4096, null=True, blank=True)),
            ('army', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auto_rosters', to=orm['tabletop.Army'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='auto_roster_user_set', to=orm['auth.User'])),
            ('pts', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tabletop', ['AutoRoster'])

        # Adding model 'Wargear'
        db.create_table(u'tabletop_wargear', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=4096, blank=True)),
            ('threshold', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('is_squad_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pts', self.gf('django.db.models.fields.PositiveIntegerField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('short_title', self.gf('django.db.models.fields.CharField')(default='unkwn', max_length=256)),
            ('limit', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('unit_amount', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal(u'tabletop', ['Wargear'])

        # Adding M2M table for field blocks on 'Wargear'
        m2m_table_name = db.shorten_name(u'tabletop_wargear_blocks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_wargear', models.ForeignKey(orm[u'tabletop.wargear'], null=False)),
            ('to_wargear', models.ForeignKey(orm[u'tabletop.wargear'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_wargear_id', 'to_wargear_id'])

        # Adding M2M table for field combines on 'Wargear'
        m2m_table_name = db.shorten_name(u'tabletop_wargear_combines')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_wargear', models.ForeignKey(orm[u'tabletop.wargear'], null=False)),
            ('to_wargear', models.ForeignKey(orm[u'tabletop.wargear'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_wargear_id', 'to_wargear_id'])

        # Adding M2M table for field model_units on 'Wargear'
        m2m_table_name = db.shorten_name(u'tabletop_wargear_model_units')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wargear', models.ForeignKey(orm[u'tabletop.wargear'], null=False)),
            ('modelunit', models.ForeignKey(orm[u'tabletop.modelunit'], null=False))
        ))
        db.create_unique(m2m_table_name, ['wargear_id', 'modelunit_id'])

        # Adding model 'UnitContainer'
        db.create_table(u'tabletop_unitcontainer', (
            ('roster', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'unit_containers', to=orm['tabletop.AutoRoster'])),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('model_unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='units', to=orm['tabletop.ModelUnit'])),
            ('pts', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tabletop', ['UnitContainer'])

        # Adding model 'WargearContainer'
        db.create_table(u'tabletop_wargearcontainer', (
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wargear_containers', to=orm['tabletop.Wargear'])),
            ('pts', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wargear_containers', to=orm['tabletop.UnitContainer'])),
        ))
        db.send_create_signal(u'tabletop', ['WargearContainer'])

        # Adding model 'Army'
        db.create_table(u'tabletop_army', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'tabletop', ['Army'])

        # Adding model 'UnitWargearRequirement'
        db.create_table(u'tabletop_unitwargearrequirement', (
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='unit_wargear_requirements', to=orm['tabletop.Wargear'])),
            ('require', self.gf('django.db.models.fields.related.ForeignKey')(related_name='unit_wargear_require_targets', to=orm['tabletop.ModelUnit'])),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('amount_target', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tabletop', ['UnitWargearRequirement'])

        # Adding model 'MWRUnit'
        db.create_table(u'tabletop_mwrunit', (
            ('threshold', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('wargear', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mwr_requirements', to=orm['tabletop.Wargear'])),
            ('model_unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requirements', to=orm['tabletop.ModelUnit'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tabletop', ['MWRUnit'])

        # Adding unique constraint on 'MWRUnit', fields ['model_unit', 'wargear']
        db.create_unique(u'tabletop_mwrunit', ['model_unit_id', 'wargear_id'])

        # Adding model 'WargearRequirement'
        db.create_table(u'tabletop_wargearrequirement', (
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wargear_requirements', to=orm['tabletop.Wargear'])),
            ('require', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wargear_require_targets', to=orm['tabletop.Wargear'])),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('threshold', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('amount_target', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tabletop', ['WargearRequirement'])


        # Changing field 'Roster.user'
        db.alter_column(u'tabletop_roster', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Roster.owner'
        db.alter_column(u'tabletop_roster', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'BattleReport.owner'
        db.alter_column(u'tabletop_battlereport', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

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
            'custom_codex': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'defeats': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_orphan': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roster_owner'", 'to': u"orm['accounts.User']"}),
            'player': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'pts': ('django.db.models.fields.IntegerField', [], {}),
            'revision': ('django.db.models.fields.IntegerField', [], {}),
            'roster': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roster_user_set'", 'null': 'True', 'to': u"orm['accounts.User']"}),
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