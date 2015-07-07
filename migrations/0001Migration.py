# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'datalocker', '0001_initial'), (b'datalocker', '0002_auto_20150624_0917'), (b'datalocker', '0003_auto_20150624_1129'), (b'datalocker', '0004_auto_20150624_1502'), (b'datalocker', '0005_auto_20150626_1620'), (b'datalocker', '0006_auto_20150629_1334')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form_url', models.CharField(max_length=255)),
                ('form_identifier', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('submitted_timestamp', models.DateTimeField(auto_now_add=True)),
                ('archive_timestamp', models.DateTimeField(null=True, editable=False, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LockerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=255)),
                ('setting', models.CharField(max_length=255)),
                ('setting_identifier', models.SlugField()),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('data', models.TextField(blank=True)),
                ('locker', models.ForeignKey(related_name='submission', db_column=b'form_identifier', on_delete=django.db.models.deletion.PROTECT, to='datalocker.Locker')),
            ],
        ),
        migrations.AddField(
            model_name='locker',
            name='owner',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='locker',
            name='users',
            field=models.ManyToManyField(related_name='lockers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RenameField(
            model_name='locker',
            old_name='submitted_timestamp',
            new_name='create_timestamp',
        ),
    ]
