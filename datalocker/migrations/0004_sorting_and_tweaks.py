# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-09-22 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0003_locker_ordering'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lockersetting',
            options={'ordering': ('locker', 'setting')},
        ),
        migrations.AlterModelOptions(
            name='submission',
            options={'ordering': ('-timestamp',)},
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='locker',
            name='form_identifier',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='locker',
            name='form_url',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='locker',
            name='name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='lockersetting',
            name='value',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='submission',
            name='data',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='submission',
            name='workflow_state',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
