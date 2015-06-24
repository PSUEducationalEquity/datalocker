# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datalocker', '0003_auto_20150624_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lockeruser',
            name='locker',
        ),
        migrations.RemoveField(
            model_name='lockeruser',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.RenameField(
            model_name='locker',
            old_name='user',
            new_name='owner',
        ),
        migrations.AddField(
            model_name='locker',
            name='users',
            field=models.ManyToManyField(related_name='lockers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='LockerUser',
        ),
    ]
