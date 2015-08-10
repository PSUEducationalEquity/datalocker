# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0005_auto_20150805_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='workflow_state',
            field=models.CharField(default=b'unreviewed', max_length=25),
        ),
    ]
