# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0003_lockersetting_locker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lockeruser',
            name='locker',
        ),
        migrations.RemoveField(
            model_name='lockeruser',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='lockersetting',
            name='locker',
        ),
        migrations.AlterField(
            model_name='submission',
            name='locker',
            field=models.ForeignKey(related_name='submission', db_column=b'form_identifier', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Locker'),
        ),
        migrations.DeleteModel(
            name='LockerUser',
        ),
    ]
