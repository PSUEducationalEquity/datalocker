# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locker',
            name='user',
            field=models.CharField(max_length=255),
        ),
    ]
