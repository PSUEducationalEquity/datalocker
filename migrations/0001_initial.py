# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(default=b'', blank=True)),
                ('parent', models.ForeignKey(related_name='children', default=None, blank=True, to='datalocker.Comment', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form_url', models.CharField(default=b'', max_length=255, blank=True)),
                ('form_identifier', models.CharField(default=b'', max_length=255, blank=True)),
                ('name', models.CharField(default=b'', max_length=255, blank=True)),
                ('create_timestamp', models.DateTimeField(auto_now_add=True)),
                ('archive_timestamp', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('owner', models.ForeignKey(related_name='lockers_owned', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('users', models.ManyToManyField(related_name='shared_lockers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LockerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=255)),
                ('setting', models.CharField(max_length=255)),
                ('identifier', models.SlugField()),
                ('value', models.TextField(default=b'')),
                ('locker', models.ForeignKey(related_name='settings', to='datalocker.Locker')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(default=b'', blank=True)),
                ('deleted', models.DateTimeField(default=None, null=True, editable=False, blank=True)),
                ('workflow_state', models.CharField(default=b'', max_length=255, blank=True)),
                ('locker', models.ForeignKey(related_name='submissions', to='datalocker.Locker')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='submission',
            field=models.ForeignKey(related_name='comments', to='datalocker.Submission'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(related_name='comments', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
