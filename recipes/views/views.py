import json
import logging
import math
import operator
import traceback
from datetime import date, datetime
from urlparse import urlparse

from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accountManaging import *
from manageRecipes import *
from recipes.models import Month, Note, RecipeUser, Text
from utils import *

PAGE_SIZE = 12

def about(request):
    context = {}
    context['text'] = Text.objects.get(name='about').text.split('\n')
    return render(request, 'about.html', context)

def menu(request):
    # url = 'http://cookieandkate.com/2014/feta-fiesta-kale-salad-with-avocado-and-crispy-tortilla-strips/'
    context = {}
    pairs = []
    get = request.GET
    start = int(get.get('start', 0))
    end = int(get.get('end', 100))

    notes = Note.objects.all()
    notes = notes[start:min(end, len(notes))]

    for note in notes:
        # context['text'] = Text.objects.get(name='about').text.split('\n')
        # recipe = parseRecipe(url)
        ingredients = note.ingredients.split('\n')
        for ingredient in ingredients:
            if not ingredient:
                continue
            parsed = getIngredientName(ingredient)
            pairs.append({
                'string': ingredient,
                'name': parsed.get('name', ''),
                'quantity': parsed.get('quantity', ''),
                'unit': parsed.get('unit', ''),
            })

    # ingredient -> unit -> [quantities]
    perIngredient = {}
    for obj in pairs:
        quantities = perIngredient.get(obj['name'], {})
        units = quantities.get(obj['unit'], [])
        units.append({'string': obj['string'], 'quantity': obj['quantity']})
        quantities[obj['unit']] = units
        perIngredient[obj['name']] = quantities

    # print json.dumps(perIngredient)

    context['ingredients'] = perIngredient


    return render(request, 'menu.html', context)

def contact(request):
    context = {}
    context['text'] = Text.objects.get(name='contact').text.split('\n')
    return render(request, 'contact.html', context)

def pagination(request, context, page, notes):
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']
    start = (page - 1) * PAGE_SIZE
    end = min(len(notes), start + PAGE_SIZE)
    pages = range(1, int(math.ceil(len(notes) / (PAGE_SIZE * 1.0))) + 1)
    context['notes'] = notes[start:end]
    context['pages'] = pages
    context['page'] = page
    context['filters'] = {}
    context['queries'] = queries_without_page
    context['previous'] = page - 1 if page - 1 > 0 else 0
    context['next'] = page + 1 if page + 1 <= len(pages) else 0
    context['rates'] = range(5, 0, -1)

def home(request):
    context = {}
    get = request.GET
    if not request.user.is_authenticated():
        context['next'] = get.get('next', '/')
        return render(request, 'welcome.html', context)
    recipeUser = getUser(request.user)
    notes = recipeUser.notes.all().order_by('-date_added')

    allNotes = recipeUser.notes.all().order_by('-date_added')

    notes_per_field = []

    page = 1
    for field in get:
        note_per_field = Note.objects.none()
        vals = get.getlist(field)
        if field == 'page':
            page = int(get.get(field))
            continue
        if field == 'rating':
            rating = int(get.get(field))
            context['ratingFilter'] = rating
            note_per_field |= recipeUser.notes.filter(rating__gte = rating)
        else:
            for val in vals:
                note_per_field |= recipeUser.notes.filter(**{field + '__icontains': val})
        notes_per_field.append(note_per_field)
    for note_per_field in notes_per_field:
        notes &= note_per_field
    pagination(request, context, page, notes)
    fields = ['tags', 'site']
    # fields = ['tags', 'site', 'rating']
    for field in fields:
        values = getTopValues(allNotes, field, get.getlist(field))
        if values:
            context['filters'][field] = values

    return render(request, 'index.html', context)

def getTopValues(notes, field, selected):
    vals = {}
    for note in notes:
        noteVals = getattr(note, field, '')
        if field == 'tags':
            noteVals = noteVals.split(',')
        else:
            noteVals = [noteVals]
        for noteVal in noteVals:
            if not noteVal:
                continue
            if not noteVal in vals:
                vals[noteVal] = 0
            vals[noteVal] += 1
    sorted_vals = sorted(vals.items(), key=operator.itemgetter(1))
    sorted_vals_els = []
    for val in sorted_vals:
        sorted_vals_els.append(val[0])
    sorted_vals_els.reverse()
    sorted_vals_els = sorted_vals_els[:10]

    elements = []
    for el in sorted_vals_els:
        elements.append({'name': el, 'selected': el in selected})
    return elements

@login_required(login_url='/')
def shareNote(request, noteId):
    recipeUser = getUser(request.user)
    try:
        note = recipeUser.notes.get(id = noteId)
    except:
        return JsonResponse({'success': False})
    setattr(note, 'shared', True)
    note.save()
    return JsonResponse({'success': True})

@login_required(login_url='/')
def note(request, noteId):
    context = {}
    recipeUser = getUser(request.user)
    note = None
    try:
        note = recipeUser.notes.get(id = noteId)
    except:
        note = get_object_or_404(Note, id = noteId)
        context['shared'] = True
        if note.shared == False or not int(request.GET.get('share', '0')):
            raise Http404("No such recipe.")
    ingredients = note.ingredients.split('\n')
    context['ingredients'] = []
    for ingredient in ingredients:
        getIngredientName(ingredient)
    context['note'] = note
    context['shareUrl'] = \
        request.build_absolute_uri('/')[:-1] + request.get_full_path() + '?share=1'
    return render(request, 'note.html', context)

@login_required(login_url='/')
def tags(request, tags):
    context = {}
    tags = tags.split(',')
    recipeUser = getUser(request.user)
    notes = Note.objects.none()
    for tag in tags:
        notes |= recipeUser.notes.filter(tags__icontains = tag)
    pagination(request, context, int(request.GET.get('page', '1')), notes)
    return render(request, 'index.html', context)

@login_required(login_url='/')
def search(request):
    context = {}
    get = request.GET
    if not get:
        return redirect('/')
    query = get.get('query', '')
    context['query'] = query
    terms = query.split(' ')
    recipeUser = getUser(request.user)
    notes = Note.objects.none()
    for term in terms:
        notes |= recipeUser.notes.filter(tags__icontains = term)
        notes |= recipeUser.notes.filter(ingredients__icontains = term)
        notes |= recipeUser.notes.filter(title__icontains = term)
        notes |= recipeUser.notes.filter(difficulty__icontains = term)
        notes |= recipeUser.notes.filter(servings__icontains = term)
        notes |= recipeUser.notes.filter(site__icontains = term)
    page = int(get.get('page', '1'))
    pagination(request, context, page, notes)
    context['no-filters'] = True
    context['success'] = ['Searched for term: ' + query]
    return render(request, 'index.html', context)

@login_required(login_url='/')
def advancedSearch(request):
    context = {}
    get = request.GET
    if not get:
        return redirect('/')
    query = get
    context['advancedQuery'] = get
    recipeUser = getUser(request.user)
    notes = Note.objects.all()
    for field in query:
        q = query.get(field, '').strip().split(',')
        if not len(q):
            continue
        for term in q:
            term = term.strip()
            if field == 'rating':
                rating = int(context['advancedQuery']['rating'])
                notes &= recipeUser.notes.filter(rating__gte = rating)
                context['rating'] = rating
            if field == 'tags':
                notes &= recipeUser.notes.filter(tags__icontains = term)
            if field == 'title':
                notes &= recipeUser.notes.filter(title__icontains = term)
            if field == 'ingredients' and not 'onlyIngredients' in query:
                notes &= recipeUser.notes.filter(ingredients__icontains = term)
            if field == 'instructions':
                notes &= recipeUser.notes.filter(instructions__icontains = term)
            if field == 'notes':
                notes &= recipeUser.notes.filter(text__icontains = term)
            if field == 'difficulty':
                notes &= recipeUser.notes.filter(difficulty__icontains = term)
            if field == 'servings':
                notes &= recipeUser.notes.filter(servings__icontains = term)
    if 'onlyIngredients' in query:
        endNotes = []
        queryIngredients = ['oil', 'salt', 'pepper', 'butter'] \
            + query.get('ingredients', '').split(',')
        for note in notes:
            if not note.ingredients:
                continue
            recipeIngredientsStr = note.ingredients.lower()
            recipeIngredients = recipeIngredientsStr.split('\n')
            inRecipe = 0
            for ingredient in queryIngredients:
                ingredient = ingredient.strip()
                if ingredient in recipeIngredientsStr:
                    inRecipe += 1
            if len(recipeIngredients) - inRecipe < 3:
                endNotes.append(note)
        notes = endNotes
    context['notes'] = notes
    context['rates'] = range(5, 0, -1)
    return render(request, 'advancedSearch.html', context)

@login_required(login_url='/')
def ingredients(request, ingredients):
    context = {}
    ingredients = ingredients.split(',')
    recipeUser = getUser(request.user)
    notes = Note.objects.none()
    for ingredient in ingredients:
        notes |= recipeUser.notes.filter(ingredients__icontains = ingredient)
    context['notes'] = notes
    return render(request, 'index.html', context)

@login_required(login_url='/')
def getSeasonRecipes(request, month):
    context = {}
    recipeUser = getUser(request.user)
    notes = Note.objects.none()

    months = Month.objects.all()
    ingredientSeasons = {}
    for m in months:
        ingredients = m.ingredients.split(',')
        for ingredient in ingredients:
            seasons = {}
            if ingredient in ingredientSeasons:
                seasons = ingredientSeasons[ingredient]
            seasons[m.index] = True
            ingredientSeasons[ingredient] = seasons

    context['ingredientSeasons'] = {}
    for ingredient in ingredientSeasons:
        months = []
        for i in range(1, 13):
            if i in ingredientSeasons[ingredient]:
                months.append(i)
            else:
                months.append(False)
        context['ingredientSeasons'][ingredient] = months
    context['months'] = ['']
    for i in range(1, 13):
        context['months'].append(date(1900, i, 1).strftime('%b'))

    if not month:
        month = datetime.now().strftime("%b")
    month = Month.objects.filter(name__icontains = month)
    if len(month):
        ingredients = month[0].ingredients.split(',')
        for ingredient in ingredients:
            if len(ingredientSeasons[ingredient]) < 6 and not ingredient == 'garlic':
                notes |= recipeUser.notes.filter(ingredients__icontains = ingredient)
        context['selected'] = date(1900, month[0].index, 1).strftime('%b')
        context['selectedIndex'] = month[0].index

    context['notes'] = notes
    return render(request, 'seasonal.html', context)

@login_required(login_url='/')
def advancedSearchHtml(request, field):
    return render(request, 'advancedSearch.html', {'rates': range(5, 0, -1)})
