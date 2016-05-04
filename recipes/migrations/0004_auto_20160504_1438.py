# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_ingredient_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='count',
            new_name='amount',
        ),
    ]
