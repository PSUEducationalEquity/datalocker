# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0005_auto_20150626_1620'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LockerSettings',
            new_name='LockerSetting',
        ),
    ]
