# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_remove_ingredient_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
