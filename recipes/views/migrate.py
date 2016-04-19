import datetime
import tldextract
import urllib2

from BeautifulSoup import BeautifulSoup, NavigableString
from django.shortcuts import render, redirect, get_object_or_404
from parse import *
from recipes.models import Recipe, Note, RecipeUser, Month

def getSeasonIngredients(request):
    url = 'http://www.bbcgoodfood.com/seasonal-calendar/all'
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
    html = urllib2.urlopen(req)
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    table = soup.find('table')
    monthLists = {}
    for i in range(12):
        monthLists[i + 1] = []

    for row in table.findAll('tr'):
        ingredient = ''
        for i, cell in enumerate(row.findAll('td')):
            if i == 0:
                ingredient = cell.find('a').text.lower()
            else:
                status = cell.find('i')
                if status:
                    status = status.text.lower()
                    monthLists[i].append(ingredient)
    for month in monthLists:
        monthObject = Month.objects.filter(index=month)
        if monthObject:
            ingredients = monthObject.ingredients.split(',')
            ingredients += monthLists[month]
            setattr(monthObject, 'ingredients', ','.join(ingredients))
        else:
            monthObject = Month.objects.create(
                index = month,
                name = datetime.date(1900, month, 1).strftime('%B'),
                ingredients = ','.join(monthLists[month])
            )
        monthObject.save()
    # for month in Month.objects.all():
    #     month.delete()
    return render(request, 'index.html', {})


def recrawlImages(request):
    context = {}
    recipes = Note.objects.all()
    for recipe in recipes:
        if not recipe.image:
            req = urllib2.Request(recipe.url, headers={'User-Agent' : "Magic Browser"})
            html = urllib2.urlopen(req)
            soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
            imageUrl = getImage(soup)
            setattr(recipe, 'image', imageUrl)
            recipe.save()
    return render(request, 'index.html', context)

def convertNotes(request):
    context = {'notes': []}
    notes = Note.objects.all()
    site = request.GET['site']
    for note in notes:
        recipe = note.recipe
        # setattr(note, 'url', recipe.url)
        # setattr(note, 'title', recipe.title)
        # setattr(note, 'image', recipe.image)
        # setattr(note, 'ingredients', recipe.ingredients)
        # setattr(note, 'instructions', recipe.instructions)
        # setattr(note, 'date_added', recipe.date_added)
        # parsed_uri = urlparse(recipe.url)
        # domain = '{uri.netloc}'.format(uri = parsed_uri)
        # setattr(note, 'site', domain)

        # extracted = tldextract.extract(note.url)
        # setattr(note, 'site', extracted.domain)

        # setattr(note, 'difficulty', Note.NONE)

        # setattr(note, 'tags', note.tags.replace('\n', ','))

        if not site in note.url:
            continue

        recipeData = parseRecipe(note.url)

        if len(recipeData['ingredients']) and note.ingredients == '':
            setattr(note, 'ingredients', '\n'.join(recipeData['ingredients']))

        if len(recipeData['instructions']) and note.instructions == '':
            setattr(note, 'instructions', '\n'.join(recipeData['instructions']))

        if 'servings' in recipeData and len(recipeData['servings']) and note.servings == '':
            setattr(note, 'servings', recipeData['servings'])

        if 'tags' in recipeData:
            setattr(note, 'tags', ','.join(recipeData['tags']))
        # date = datetime.strptime(recipe.date_added, "%Y-%m-%d %H:%M:%S.%f")
        # setattr(note, 'created_at', date)
        note.save()
        context['notes'].append(note)
    return render(request, 'index.html', context)
