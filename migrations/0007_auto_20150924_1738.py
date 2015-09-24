# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0006_auto_20150806_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locker',
            name='users',
            field=models.ManyToManyField(related_name='lockers', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='workflow_state',
            field=models.CharField(default=b'', max_length=25, blank=True),
        ),
    ]
