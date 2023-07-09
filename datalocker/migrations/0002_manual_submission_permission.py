# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datalocker', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locker',
            options={'permissions': (('add_manual_submission', 'Can add manual submission'),)},
        ),
    ]
