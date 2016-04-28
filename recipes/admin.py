from django.contrib import admin

from recipes.models import Note, RecipeUser, Month, Strings

admin.site.register(RecipeUser)
admin.site.register(Note)
admin.site.register(Strings)
