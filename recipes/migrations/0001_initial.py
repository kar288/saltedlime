# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('amount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('index', models.IntegerField()),
                ('ingredients', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('difficulty', models.CharField(default='-', max_length=1, choices=[('H', 'Hard'), ('M', 'Medium'), ('E', 'Easy'), ('-', '-')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.CharField(max_length=200, db_index=True)),
                ('title', models.CharField(max_length=400)),
                ('image', models.CharField(max_length=400)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('date_added', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('tags', models.TextField()),
                ('rating', models.IntegerField()),
                ('servings', models.CharField(max_length=400)),
                ('site', models.CharField(max_length=200, null=True)),
                ('shared', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=400)),
                ('image', models.CharField(max_length=400)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('date_added', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profilePic', models.CharField(max_length=400, null=True)),
                ('name', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('facebookUser', models.OneToOneField(related_name='facebookUser', null=True, to=settings.AUTH_USER_MODEL)),
                ('googleUser', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
                ('notes', models.ManyToManyField(to='recipes.Note')),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('text', models.TextField()),
            ],
        ),
    ]
