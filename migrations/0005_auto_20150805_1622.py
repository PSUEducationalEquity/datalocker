# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0004_auto_20150722_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='workflow_state',
            field=models.CharField(max_length=25, blank=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='deleted',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
