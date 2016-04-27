from django.contrib import admin

from recipes.models import Note, RecipeUser, Month

admin.site.register(RecipeUser)
admin.site.register(Note)
