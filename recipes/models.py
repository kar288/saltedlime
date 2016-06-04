from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

import tldextract

class DayMenu(models.Model):
    date = models.DateField()
    notes = models.TextField(default='')
    name = models.CharField(max_length=200, null=True)

class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    amount = models.IntegerField(default=0)

class Text(models.Model):
    name = models.CharField(unique=True, max_length=200)
    text = models.TextField()
    def __unicode__(self):
        return u'%s' % self.name
    def __str__(self):
        return self.name

class Month(models.Model):
  name = models.CharField(max_length=20)
  index = models.IntegerField()
  ingredients = models.TextField()

class Recipe(models.Model):
  url = models.CharField(max_length=200)
  title = models.CharField(max_length=400)
  image = models.CharField(max_length=400)
  ingredients = models.TextField()
  instructions = models.TextField()
  date_added = models.CharField(max_length=200)
  def ingredients_as_list(self):
    return self.ingredients.split('\n')
  def instructions_as_list(self):
    return self.instructions.split('\n')

class Note(models.Model):
    HARD = 'H'
    MEDIUM = 'M'
    EASY = 'E'
    NONE = '-'
    DIFFICULTY_MAP = {
        HARD: 0,
        MEDIUM: 1,
        EASY: 2,
        NONE: 3,
    }
    RECIPE_DIFFICULTY = (
        (HARD, 'Hard'),
        (MEDIUM, 'Medium'),
        (EASY, 'Easy'),
        (NONE, '-'),
    )
    difficulty = models.CharField(max_length=1,
        choices=RECIPE_DIFFICULTY,
        default=NONE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(db_index=True, max_length=200)
    title = models.CharField(max_length=400)
    image = models.CharField(max_length=400)
    ingredients = models.TextField()
    instructions = models.TextField()
    date_added = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.TextField()
    rating = models.IntegerField()
    servings = models.CharField(max_length=400)
    site = models.CharField(max_length=200, null=True)
    shared = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    def __unicode__(self):
        return u'%s' % self.title
    def difficulty_long(self):
        if self.difficulty == '':
            return '-'
        return self.RECIPE_DIFFICULTY[self.DIFFICULTY_MAP[self.difficulty]][1]
    def tags_as_list(self):
        tags = self.tags.replace('\r', '').split(',')
        newTags = []
        for tag in tags:
            newTags.append(tag.strip())
        return [tag for tag in tags if len(tag)]
    def rating_as_list(self):
        return range(self.rating)
    def ingredients_as_list(self):
        return self.ingredients.split('\n')
    def instructions_as_list(self):
        return [row.split() for row in self.instructions.split('\n')]
    def title_short(self):
        return self.title[:30]
    def date_added_formatted(self):
        # return self.date_added
        return self.created_at.strftime("%d/%b/%y")
    def siteLink(self):
        parts = tldextract.extract(self.url)
        return '//' + parts.domain + '.' + parts.suffix

class RecipeUser(models.Model):
  googleUser = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
  facebookUser = models.OneToOneField(User,related_name='facebookUser', on_delete=models.CASCADE, null=True)
  profilePic = models.CharField(max_length=400, null=True)
  name = models.CharField(max_length=200, null=True)
  email = models.CharField(max_length=200, null=True)
  notes = models.ManyToManyField(Note)
  menus = models.ManyToManyField(DayMenu)

  def __str__(self):
      return self.name
  def __unicode__(self):
      return u'%s' % self.name
