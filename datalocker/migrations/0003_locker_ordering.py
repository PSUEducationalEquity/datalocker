# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0002_manual_submission_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locker',
            options={'ordering': ('name',), 'permissions': (('add_manual_submission', 'Can add manual submission'),)},
        ),
    ]
