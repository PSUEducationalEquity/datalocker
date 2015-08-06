# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0005_auto_20150806_0819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='parent_comment',
            field=models.ForeignKey(related_name='comment_parent', blank=True, to='datalocker.Comments', null=True),
        ),
    ]
