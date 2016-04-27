# from accountManaging import *
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from parse import *
from recipes.models import Note, RecipeUser
from urlparse import urlparse
from utils import *

import json
import math
import socket

def getTagsForNote(note):
    tags = ['breakfast', 'lunch', 'dinner', 'snack', 'vegetarian', 'vegan']
    text = note.title
    words = text.split(' ')
    longerWords = [word.lower() for word in words if len(word) > 2 and word[-3:] != 'ing']
    return longerWords + tags

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
def addRecipeHtml(request):
    return render(request, 'addRecipe.html', {
        'rates': range(5, 0, -1),
        'note': {'rating': -1}
    })

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


def addRecipeByUrl(recipeUser, recipeUrl, post):
    socket.setdefaulttimeout(30)
    logger.info(recipeUrl)
    if recipeUrl and recipeUser.notes.filter(url = recipeUrl).exists():
        logger.info(recipeUrl + ' Recipe exists')
        return {'error': 'Recipe already exists!', 'level': 0}
    try:
        domain = ''
        recipeData = {}
        if recipeUrl:
            recipeData = parseRecipe(recipeUrl)
            domain = 'manual'
            if not recipeData or len(recipeData) == 1:
                return {'error': 'Empty recipe?', 'level': 3}
            domain = tldextract.extract(recipeUrl).domain
        tags = ','.join(recipeData.get('tags', []))
        if post.get('tags', ''):
            tags += ',' + post.get('tags', '')
        title = recipeData.get('title', post.get('title', ''))
        if not len(title):
            return {'error': 'This recipe has a missing title or other essential information. Try adding it manually.', 'level': 3}
        note = Note.objects.create(
          url = recipeUrl,
          image = recipeData.get('image', post.get('image', '')),
          ingredients = recipeData.get('ingredients', post.get('ingredients', '')),
          instructions = recipeData.get('instructions', post.get('instructions', '')),
          title = title[:200],
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
    except:
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
    post = request.POST
    if not post:
        return JsonResponse({})
    urls = json.loads(post.get('urls'))
    data = []
    recipeUser = getUser(request.user)
    for url in urls:
        if not url:
            continue

        u = url['url']
        if recipeUser.notes.filter(url = u).exists():
            data.append(url['index'])
    return JsonResponse({'data': data})

@login_required(login_url='/')
def processBulk(request):
    start = datetime.now()
    context = {}
    post = request.POST
    cookingDomains = {
        'food52': True,
        'smittenkitchen': True,
        'thekitchn.com': True,
        'www.epicurious': True,
        'allrecipes': True,
        'cooking.nytimes': True,
        'food': True,
        '101cookbooks': True,
        'marthastewart': True,
        'jamieoliver': True,
        'allrecipes': True,
    }
    if not post or not 'bookmarks' in request.FILES:
        logger.info('No bookmarks file')
        return render(request, 'addRecipes.html', context)
    if not request.FILES['bookmarks'].name.endswith('.html'):
        logger.info('Bookmarks not an html file: ' + request.FILES['bookmarks'].name)
        return render(request, 'addRecipes.html',
            {'errors': [{'error': 'Please upload an html file'}]})

    recipeUser = getUser(request.user)
    try:
        bookmarks = request.FILES['bookmarks'].read()
        soup = BeautifulSoup(bookmarks, "html.parser")
        urls = []
        done = 0
        tags = soup.findAll('a')
        if len(tags) == 0:
            logger.info('No bookmarks in file: ' + request.FILES['bookmarks'].name)
            return render(request, 'addRecipes.html',
                {'errors': [{'error': 'No bookmarks or links in the file!'}]})
        print len(tags)
        for tag in tags:
            href = normalizeURL(tag.get('href'))
            text = tag.text if tag.text else href
            urls.append({
                'url': href,
                'name': text,
                'color': '#C8E6C9' if 'recipe' in text.lower() else ''
            })
        context['urls'] = urls
        context['done'] = done

        context['pages'] = []
        for i in range(int(math.ceil(len(urls) / 100)) + 1):
            context['pages'].append( \
                urls[i * 100 : min((i + 1) * 100, len(urls))])
    except Exception as e:
        logger.exception(e)
        return render(request, 'addRecipes.html',
            {'errors': [{'error' : 'Invalid bookmark file'}]})
    logger.info('Processing bulk time: ' + str((datetime.now() - start).seconds))
    return render(request, 'addRecipes.html', context)


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
    note.save()
    recipeUser.notes.add(note)
    return redirect('/note/' + str(note.id))
