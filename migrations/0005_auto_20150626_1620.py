# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0004_auto_20150624_1502'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locker',
            old_name='submitted_timestamp',
            new_name='create_timestamp',
        ),
        migrations.AlterField(
            model_name='submission',
            name='locker',
            field=models.ForeignKey(related_name='submission', db_column=b'form_identifier', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Locker'),
        ),
    ]
