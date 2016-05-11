# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20160508_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='name',
            field=models.CharField(unique=True, max_length=200),
        ),
    ]
