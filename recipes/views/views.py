# from django.http import HttpResponse
# from mimetypes import guess_type
# from django.conf import settings
# import csv
# import re
# from random import randint
# from topia.termextract import tag
# from topia.termextract import extract
# import urllib2
# import tldextract
# import xml.etree.ElementTree as ET
# from django.template import loader
# from django.shortcuts import redirect
# from social.backends.oauth import BaseOAuth1, BaseOAuth2
# from social.backends.google import GooglePlusAuth
# from social.backends.utils import load_backends
# from social.apps.django_app.utils import psa
# from  django.db.models import Q
# import re
# from BeautifulSoup import BeautifulSoup, NavigableString

from datetime import datetime, date
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.clickjacking import xframe_options_exempt
from parse import *
from recipes.models import Recipe, Note, RecipeUser, Month
from urlparse import urlparse

import hashlib
import logging
import math
import operator
import requests
import socket
import sys
import traceback

PAGE_SIZE = 12

logger = logging.getLogger('recipesParsing')

def getTableFields(field, direction):
    fields =  [{
            'field': 'image',
            'display': '',
            'selected': direction if 'image' == field else 0
        }, {
            'field': 'title',
            'display': 'Title',
            'selected': direction if 'title' == field else 0
        }, {
            'field': 'site',
            'display': 'Site',
            'selected': direction if 'site' == field else 0
        }, {
            'field': 'difficulty',
            'display': 'Difficulty',
            'selected': direction if 'difficulty' == field else 0
        }, {
            'field': 'servings',
            'display': 'Servings',
            'selected': direction if 'servings' == field else 0
        }, {
            'field': 'rating',
            'display': 'Rating',
            'selected': direction if 'rating' == field else 0
        }, {
            'field': 'created_at',
            'display': 'Date',
            'selected': direction if 'rating' == field else 0
        }]
    return fields

def normalizeURL(url):
    if not url[-1] == '/':
        return url + '/'
    return url

def getUser(user):
    recipeUser = RecipeUser.objects.filter(googleUser = user) | RecipeUser.objects.filter(facebookUser = user)
    if not recipeUser.exists():
        raise Http404("No such user.")
    return recipeUser[0]

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

# @xframe_options_exempt
def home(request):
    context = {}
    if not request.user.is_authenticated():
        return render(request, 'recipeBase.html', context)
    print request.user
    # auth_logout(request)
    recipeUser = getUser(request.user)
    notes = recipeUser.notes.all().order_by('-date_added')

    allNotes = recipeUser.notes.all().order_by('-date_added')

    get = request.GET
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

def doneLogin(request):
    return render(request, 'doneLogin.html', {})

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
def table(request, field, direction):
    context = {}
    field = field if field else 'title'
    recipeUser = getUser(request.user)

    if field == 'rating' or field == 'created_at':
        context['notes'] = recipeUser.notes.all().order_by(field)
    else:
        context['notes'] = recipeUser.notes.all().order_by(Lower(field))

    direction = int(direction)
    if direction == 1:
        context['notes'] = context['notes'].reverse()
    if direction == 1:
        direction = 2
    elif direction == 2 or direction == 0:
        direction = 1
    context['fields'] = getTableFields(field, direction)
    return render(request, 'table.html', context)

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
def addSharedRecipe(request, noteId):
    recipeUser = getUser(request.user)
    try:
        note = recipeUser.notes.find(id = noteId)
        return redirect('/note/' + noteId)
    except:
        try:
            note = get_object_or_404(Note, id = noteId)
            if not note.shared:
                context = {}
                context['errors'] = ['No such recipe']
                return redirect('/')
        except:
            context = {}
            context['errors'] = ['No such recipe']
            return redirect('/')
    note.pk = None
    # recipe = note.recipe
    # recipe.pk = None
    # recipe.save()
    # note.recipe = recipe
    note.save()
    recipeUser.notes.add(note)
    return redirect('/note/' + str(note.id))

@login_required(login_url='/')
def tableAll(request, field):
    context = {}
    field = field if field else 'title'
    context['notes'] = Note.objects.all().order_by(Lower(field))
    context['fields'] = getTableFields(field, 1)
    return render(request, 'table.html', context)

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
    for note in notes:
        print note.url
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
    # context['success'] = ingredients
    return render(request, 'seasonal.html', context)


@login_required(login_url='/')
def editNoteHtml(request, noteId):
    context = {'edit': True, 'rates': range(5, 0, -1)}
    recipeUser = getUser(request.user)
    note = get_object_or_404(Note, id = noteId)
    context['tags'] = getTagsForNote(note)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        context['note'] = note
    return render(request, 'note.html', context)

@login_required(login_url='/')
def deleteNoteHtml(request, noteId):
    context = {}
    recipeUser = getUser(request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        context['note'] = note
    return render(request, 'deleteNote.html', context)

def deleteNote(request, noteId):
    context = {}
    recipeUser = getUser(request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        recipe = note.recipe
        context['success'] = ['Recipe was deleted: ' + note.title]
        if recipe:
            recipe.delete()
        note.delete()
        context['notes'] = recipeUser.notes.all()
    return redirect('/')

def deleteRecipes(request):
    context = {}
    get = request.GET
    ids = get.getlist('recipe')
    recipeUser = getUser(request.user)
    for noteId in ids:
        try:
            note = recipeUser.notes.get(id = noteId)
        except:
            context['errors'] = ['Note not found']
        recipe = note.recipe
        context['success'] = ['Recipe was deleted: ' + note.title]
        if recipe:
            recipe.delete()
        note.delete()
    return redirect('/table/title/1')

@login_required(login_url='/')
def advancedSearchHtml(request, field):
    return render(request, 'advancedSearch.html', {'rates': range(5, 0, -1)})

@login_required(login_url='/')
def addRecipeHtml(request):
    return render(request, 'addRecipe.html', {
        'rates': range(5, 0, -1),
        'note': {'rating': -1}
    })

@login_required(login_url='/')
def addRecipesHtml(request):
    return render(request, 'addRecipes.html')

def addRecipeAsync(request):
    context = {}
    get = request.GET
    url = get.get('url', '')
    recipeUser = getUser(request.user)
    try:
        context['error'] = addRecipeByUrl(recipeUser, url, get)
    except:
        context['error'] = {'error': 'An unexpected error occured!', 'level': 2}
    return JsonResponse(context)

def editNote(request, noteId):
    context = {}
    post = request.POST
    if not post:
        return redirect('/note/' + noteId)
    recipeUser = getUser(request.user)
    note = get_object_or_404(Note, id = noteId)
    if not note in recipeUser.notes.all():
        context['errors'] = ['Note not found']
    else:
        for field in post:
            if not field == 'difficulty' and not field == 'rating':
                setattr(note, field, clean(post.get(field, '')))
        setattr(note, 'rating', post.get('rating', -1))
        setattr(note, 'difficulty', post.get('difficulty', '-'))
        note.save()
        context['note'] = note
    return redirect('/note/' + noteId)

def clean(str):
    return str.replace('\r', '').strip()

def addNote(request):
    post = request.POST
    if not post:
        return redirect('/addRecipe/')
    recipeUser = getUser(request.user)
    recipeUrl = post['recipeUrl']
    error = addRecipeByUrl(recipeUser, recipeUrl, post)
    if error:
        return render(request, 'addRecipe.html', {'errors': [error]})
    return redirect('/')

def getTagsForNote(note):
    tags = ['breakfast', 'lunch', 'dinner', 'snack', 'vegetarian', 'vegan']
    text = note.title
    words = text.split(' ')
    longerWords = [word.lower() for word in words if len(word) > 2 and word[-3:] != 'ing']
    return longerWords + tags

def addRecipeByUrl(recipeUser, recipeUrl, post):
    print 'logging'
    socket.setdefaulttimeout(30)
    logger.info(recipeUrl)
    if recipeUser.notes.filter(url = recipeUrl).exists():
        logger.info(recipeUrl + ' Recipe exists')
        return {'error': 'Recipe already exists!', 'level': 0}
    try:
        domain = ''
        recipeData = {}
        print recipeUrl
        if recipeUrl:
            recipeData = parseRecipe(recipeUrl)
            if not recipeData or len(recipeData) == 1:
                return {'error': 'Empty recipe?', 'level': 3}
            domain = tldextract.extract(recipeUrl).domain
        # recipe = Recipe.objects.create(
        #   url = recipeUrl,
        #   image = image,
        #   ingredients = ingredients,
        #   instructions = instructions,
        #   title = title[:200],
        #   date_added = datetime.now()
        # )
        tags = ','.join(recipeData.get('tags', []))
        if post.get('tags', ''):
            tags += ',' + post.get('tags', '')
        note = Note.objects.create(
        #   recipe = recipe,
          url = recipeUrl,
          image = recipeData.get('image', post.get('image', ''))[:400],
          ingredients = recipeData.get('ingredients', post.get('ingredients', '')),
          instructions = recipeData.get('instructions', post.get('instructions', '')),
          title = recipeData.get('title', post.get('title', 'No name'))[:200],
          date_added = datetime.now(),
          text = post.get('notes', ''),
          tags = tags,
          rating = post.get('rating', -1),
          site = domain,
          difficulty = post.get('difficulty', ''),
          servings = recipeData.get('servings', post.get('servings', ''))[:100]
        )
        recipeUser.notes.add(note)
    except urllib2.URLError, err:
        traceback.print_exc()
        logger.exception('urlerror')
        if 'code' in err and err.code == 404:
            return {'error': 'The recipe was not found, it might have been removed!', \
                'level': 3 }
        return {'error': 'Could not get recipe. The site might be down.', 'level': 3}
    except urllib2.HTTPError, err:
        traceback.print_exc()
        logger.exception('httperror')
        if err.code == 404:
            return {'error': 'The rcipe was not found, it might have been removed!', 'level': 3}
        return {'error': 'Could not get recipe. The site might be down.', 'level': 3}
    except socket.timeout:
        logger.exception('timeout')
        return {'error': 'It took too long to get recipe. The site might be down.', 'level': 3}
    except Exception:
        logger.exception('another exception')
        traceback.print_exc()
        return {'error': sys.exc_info()[0], 'level': 3}

@login_required(login_url='/')
def addBulk(request):
    context = {'errors': []}
    post = request.POST
    if not post:
        return redirect('/add')
    bookmarks = post.getlist('bookmark')

    rendered = render_to_string('addRecipesList.html', {'recipes': bookmarks})
    return JsonResponse({'rendered': rendered})

@login_required(login_url='/')
def recipeExists(request):
    get = request.GET
    url = get.get('url')
    if not url:
        return JsonResponse({'exists': False})
    recipeUser = getUser(request.user)
    return JsonResponse({'exists': recipeUser.notes.filter(url = url).exists()})

@login_required(login_url='/')
def processBulk(request):
    start = datetime.now()
    context = {}
    post = request.POST
    cookingDomains = {
        'food52.com': True,
        'smittenkitchen.com': True,
        'www.thekitchn.com': True,
        'www.epicurious.com': True,
        'allrecipes.com': True,
        'cooking.nytimes.com': True,
        'www.food.com': True,
        'www.101cookbooks.com': True,
        'www.marthastewart.com': True,
        'www.jamieoliver.com': True,
        'allrecipes.com': True,
    }
    if not post or not 'bookmarks' in request.FILES:
        logger.info('No bookmarks file')
        return render(request, 'addRecipes.html', context)
    if not request.FILES['bookmarks'].name.endswith('.html'):
        logger.info('Bookmarks not an html file: ' + request.FILES['bookmarks'].name)
        return render(request, 'addRecipes.html', {'errors': [{'error': 'Please upload an html file'}]})

    recipeUser = getUser(request.user)
    try:
        bookmarks = request.FILES['bookmarks'].read()
        soup = BeautifulSoup(bookmarks, "html.parser")
        urls = []
        done = 0
        tags = soup.findAll('a')
        if len(tags) == 0:
            logger.info('No bookmarks in file: ' + request.FILES['bookmarks'].name)
            return render(request, 'addRecipes.html', {'errors': [{'error': 'No bookmarks or links in the file!'}]})
        print len(tags)
        for tag in tags:
            href = normalizeURL(tag.get('href'))
            text = tag.text if tag.text else href
            if (datetime.now() - start).seconds < 20 and recipeUser.notes.filter(url = href):
            # if done < 0 and recipeUser.notes.filter(url = href):
                done += 1
            else:
                parsed_uri = urlparse(href)
                domain = '{uri.netloc}'.format(uri=parsed_uri)
                color = 'white'
                if domain in cookingDomains or 'recipe' in text.lower():
                    color = 'rgba(38, 166, 154, 0.3)'
                urls.append({
                    'url': href,
                    'name': text,
                    'color': color
                })
        context['urls'] = urls
        context['done'] = done
        context['pages'] = []
        for i in range(int(math.ceil(len(urls) / 10)) + 1):
            context['pages'].append( \
                urls[i * 10 : min((i + 1) * 10, len(urls))])
        context['stepSize'] = 100.0 / len(context['pages'])
    except Exception as e:
        logger.exception(e)
        return render(request, 'addRecipes.html', {'errors': ['Invalid bookmark file']})
    logger.info('Processing bulk time: ' + str((datetime.now() - start).seconds))
    return render(request, 'addRecipes.html', context)


def save_profile_picture(strategy, user, response, details,
                         is_new=False,*args,**kwargs):
    profile = user.userprofile
    profile.profile_photo.save('{0}_social.jpg'.format(user.username),
                           ContentFile(response.content))
    profile.save()

def save_profile(backend, user, response, *args, **kwargs):
  # print user.__class__;
  # print kwargs['social']
    # print response
    data = {}
    if backend.name == "google-oauth2":
        data['profilePic'] = response.get('image', {}).get('url', None)
        data['name'] = response.get('displayName', None)
        data['email'] = response.get('emails', [{}])[0].get('value', None)
        data['googleUser'] = user
        recipeUser = RecipeUser.objects.filter(googleUser = user)
    elif backend.name == 'facebook':
        if 'id' in response:
            data['profilePic'] = 'http://graph.facebook.com/' + response['id'] + '/picture?type=square'
        data['name'] = response.get('name', None)
        data['email'] = response.get('email', None)
        data['facebookUser'] = user
        recipeUser = RecipeUser.objects.filter(facebookUser = user)

    if not recipeUser.exists():
        userByEmail = RecipeUser.objects.filter(email = data['email'])
        if userByEmail.exists():
            logging.info('email exists, joining account')
            recipeUser = userByEmail
        else:
            RecipeUser.objects.create(
                googleUser = data.get('googleUser', None),
                facebookUser = data.get('facebookUser', None),
                profilePic = data.get('profilePic', None),
                name = data.get('name', None),
                email = data.get('email', None)
            )
            return;
    recipeUser = recipeUser[0]
    changed = False
    for attr in data:
        if not getattr(recipeUser, attr) and data[attr]:
            setattr(recipeUser, attr, data[attr])
            changed = True
    if changed:
        recipeUser.save()

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def facebook_phone(request):
    return render(request, 'facebook_phone.html')

api_version = "v1.0"
app_id = ''
app_secret = '';
me_endpoint_base_url = 'https://graph.accountkit.com/v1.0/me';
token_exchange_base_url = 'https://graph.accountkit.com/v1.0/access_token';
import hmac
import hashlib
import base64

def genAppSecretProof(app_secret, access_token):
    h = hmac.new (
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()

def accountkit_login(request):
    app_access_token = '|'.join(['AA', app_id, app_secret])
    print app_access_token
    params = \
        'grant_type=' + 'authorization_code' + \
        '&code=' + request.POST.get('code') + \
        '&access_token=' + app_access_token

    token_exchange_url = token_exchange_base_url + '?' + params;
    print token_exchange_url
    response = requests.get(token_exchange_url)
    data = response.json()
    # Request.get({url: token_exchange_url, json: true}, function(err, resp, respBody) {
    #   var view = {
    #     user_access_token: respBody.access_token,
    #     expires_at: respBody.expires_at,
    #     user_id: respBody.id,
    #   };
    #
    #   // get account details at /me endpoint
    print data

    appsecret_proof = genAppSecretProof('', data['access_token'])
    me_endpoint_url = me_endpoint_base_url + '?access_token=' + data['access_token'] + '&appsecret_proof=' + appsecret_proof;
    me_endpoint_url = me_endpoint_base_url + '?access_token=' + data['access_token'];
    print me_endpoint_url
    response = requests.get(me_endpoint_url)
    print response.text
    #   Request.get({url: me_endpoint_url, json:true }, function(err, resp, respBody) {
    #     // send login_success.html
    #     if (respBody.phone) {
    #       view.phone_num = respBody.phone.number;
    #     } else if (respBody.email) {
    #       view.email_addr = respBody.email.address;
    #     }
    #     var html = Mustache.to_html(loadLoginSuccess(), view);
    #     response.send(html);
    #   });
    # });
    return render(request, 'index.html')
