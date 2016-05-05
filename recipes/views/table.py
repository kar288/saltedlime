from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from recipes.models import Note, RecipeUser
from utils import *


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
            'selected': direction if 'created_at' == field else 0
        }]
    return fields


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
def tableAll(request, field):
    context = {}
    field = field if field else 'title'
    context['notes'] = Note.objects.all().order_by(Lower(field))
    context['fields'] = getTableFields(field, 1)
    return render(request, 'table.html', context)
