from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import recipes.views

# Examples:
# url(r'^$', 'project.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', recipes.views.home, name='recipesHome'),
    url("^soc/", include("social.apps.django_app.urls", namespace="social")),
    url(r'^login/$', recipes.views.home),
    url(r'^logout/$', recipes.views.logout, name='logout'),
    url(r'^done/$', recipes.views.home, name='done'),
    url(r'^getSeasonIngredients/$', recipes.views.getSeasonIngredients, name='getSeasonIngredients'),
    url(r'^season/(?P<month>[\w]+)?/$', recipes.views.getSeasonRecipes, name='season'),
    url(r'^recrawlImages/$', recipes.views.recrawlImages, name='recrawlImages'),
    url(r'^convertNotes/$', recipes.views.convertNotes, name='convertNotes'),
    url(r'^addNote/$', recipes.views.addNote, name='addNote'),
    url(r'^addBulk/$', recipes.views.addBulk, name='addBulk'),
    url(r'^recipeExists/$', recipes.views.recipeExists, name='recipeExists'),
    url(r'^processBulk/$', recipes.views.processBulk, name='processBulk'),
    url(r'^addRecipe/$', recipes.views.addRecipeHtml, name='addRecipe'),
    url(r'^addRecipeAsync/$', recipes.views.addRecipeAsync, name='addRecipeAsync'),
    url(r'^addRecipes/$', recipes.views.addRecipesHtml, name='addRecipes'),
    url(r'^note/(?P<noteId>[0-9]+)/$', recipes.views.note, name='note'),
    url(r'^tags/(?P<tags>.+)/$', recipes.views.tags, name='tags'),
    url(r'^search/$', recipes.views.search, name='search'),
    url(r'^accountkit_login/$', recipes.views.accountkit_login, name='accountkit_login'),
    url(r'^facebook_phone/$', recipes.views.facebook_phone, name='facebook_phone'),
    url(r'^doneLogin/$', recipes.views.doneLogin, name='doneLogin'),
    url(r'^about/$', recipes.views.about, name='about'),
    url(r'^contact/$', recipes.views.contact, name='contact'),
    url(r'^table/(?P<field>[\w]*)/(?P<direction>[0-9]*)/$', recipes.views.table, name='table'),
    url(r'^tableAll/(?P<field>[\w]*)/$', recipes.views.tableAll, name='tableAll'),
    url(r'^advancedSearch/$', recipes.views.advancedSearch, name='advancedSearch'),
    url(r'^advancedSearchHtml/(?P<field>[\w]*)/$', recipes.views.advancedSearchHtml, name='advancedSearchHtml'),
    url(r'^ingredients/(?P<ingredients>[\w,]+)/$', recipes.views.ingredients, name='ingredients'),
    url(r'^editNote/(?P<noteId>[0-9]+)/$', recipes.views.editNote, name='editNote'),
    url(r'^shareNote/(?P<noteId>[0-9]+)/$', recipes.views.shareNote, name='shareNote'),
    url(r'^addSharedRecipe/(?P<noteId>[0-9]+)/$', recipes.views.addSharedRecipe, name='addSharedRecipe'),
    url(r'^editNoteHtml/(?P<noteId>[0-9]+)/$', recipes.views.editNoteHtml, name='editNoteHtml'),
    url(r'^deleteNote/(?P<noteId>[0-9]+)/$', recipes.views.deleteNote, name='deleteNote'),
    url(r'^deleteNoteHtml/(?P<noteId>[0-9]+)/$', recipes.views.deleteNoteHtml, name='deleteNoteHtml'),
    url(r'^deleteRecipes/$', recipes.views.deleteRecipes, name='deleteRecipes'),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
