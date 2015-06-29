# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0006_merge'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LockerSettings',
            new_name='LockerSetting',
        ),
    ]
