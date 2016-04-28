from django.contrib import admin

from recipes.models import Note, RecipeUser, Month, Text

admin.site.register(RecipeUser)
admin.site.register(Note)
admin.site.register(Text)
