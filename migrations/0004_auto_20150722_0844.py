# -*- coding: utf-8 -*-
### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0003_lockersetting_locker'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='deleted',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='lockersetting',
            name='locker',
            field=models.ForeignKey(related_name='settings', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Locker'),
        ),
    ]
