# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datalocker', '0005_auto_20150805_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(blank=True)),
                ('parent_comment', models.ForeignKey(related_name='comment_parent', to='datalocker.Comment')),
            ],
        ),
        migrations.AlterField(
            model_name='submission',
            name='deleted',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='submission',
            field=models.ForeignKey(related_name='comments', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Submission'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(related_name='comment_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
