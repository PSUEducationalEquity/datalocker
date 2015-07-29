# -*- coding: utf-8 -*- #
### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='locker',
            field=models.ForeignKey(related_name='submissions', db_column=b'form_identifier', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Locker'),
        ),
    ]
