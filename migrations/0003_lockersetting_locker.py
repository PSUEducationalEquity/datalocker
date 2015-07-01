# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0002_auto_20150701_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockersetting',
            name='locker',
            field=models.ForeignKey(related_name='settings', on_delete=django.db.models.deletion.PROTECT, default=None, to='datalocker.Locker'),
            preserve_default=False,
        ),
    ]
