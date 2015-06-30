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
            name='Locker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form_url', models.CharField(max_length=255)),
                ('form_identifier', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.CharField(max_length=255)),
                ('create_timestamp', models.DateTimeField(auto_now_add=True)),
                ('archive_timestamp', models.DateTimeField(null=True, editable=False, blank=True)),
                ('users', models.ManyToManyField(related_name='lockers', to=settings.AUTH_USER_MODEL)),
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
    ]
