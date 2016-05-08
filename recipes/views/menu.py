import collections
from datetime import date, datetime, timedelta
from fractions import Fraction

from django.shortcuts import get_object_or_404, redirect, render

from parse import *
from utils import *

dayFormat = '%d-%B-%Y'
dayFormatHR = '%A %B, %-d'

def addToMenu(request):
    get = request.GET
    dayString = get.get('day', '')
    note = get.get('note', '')
    if not dayString or not note:
        return redirect('/menu')

    recipeUser = getUser(request.user)
    day =  datetime.strptime(dayString, dayFormat)
    dayMenu, created = recipeUser.menus.get_or_create(date = day)
    if created:
        recipeUser.menus.add(dayMenu)
    notes = dayMenu.notes.split()
    if not note in notes:
        notes.append(note)
        setattr(dayMenu, 'notes', ' '.join(notes))
        dayMenu.save()

    return redirect('/menu')

def deleteFromMenu(request):
    get = request.GET
    dayString = get.get('day', '')
    note = get.get('note', '')
    if not dayString or not note:
        return redirect('/menu')

    recipeUser = getUser(request.user)
    day =  datetime.strptime(dayString, dayFormat)
    try:
        dayMenu = recipeUser.menus.get(date = day)
        notes = dayMenu.notes.split()
        notes.remove(note)
        setattr(dayMenu, 'notes', ' '.join(notes))
        dayMenu.save()
    except:
        return redirect('/menu')

    return redirect('/menu')

def menu(request):
    context = {}
    pairs = []
    get = request.GET
    ids = get.getlist('id', [])

    notes = Note.objects.none()

    context['week'] = []
    recipeUser = getUser(request.user)
    for i in range(7):
        currentData = datetime.now() + timedelta(i)
        try:
            dayMenu = recipeUser.menus.get(date = currentData)
        except:
            context['week'].append({
                'date': currentData.strftime(dayFormat),
                'dateString': currentData.strftime(dayFormatHR)
            })
            continue
        menu = None
        menuNotes = []
        noteIds = dayMenu.notes.split()
        for noteId in noteIds:
            note = recipeUser.notes.filter(id = noteId)
            notes |= note
            menuNotes.append(note[0])
        context['week'].append({
            'date': currentData.strftime(dayFormat),
            'dateString': currentData.strftime(dayFormatHR),
            'notes': menuNotes
        })

    for note in notes:
        ingredients = note.ingredients.split('\n')
        for ingredient in ingredients:
            if not ingredient:
                continue
            parsed = getIngredientName(ingredient)
            pairs.append({
                'string': ingredient,
                'name': parsed.get('name', 'unknown'),
                'quantity': parsed.get('quantity', ''),
                'unit': parsed.get('unit', ''),
                'note': note.id,
                'title': note.title
            })

    # ingredient -> unit -> [quantities]
    perIngredient = {}
    for obj in pairs:
        quantities = perIngredient.get(obj['name'], {})
        units = quantities.get(obj['unit'], {})
        details = units.get('details', [])
        total = units.get('total', 0)
        details.append({
            'string': obj['string'],
            'quantity': obj['quantity'],
            'note': obj['note'],
            'title': obj['title']
        })
        quantity = obj['quantity']
        parts = quantity.strip().split(' ')
        for part in parts:
            if part and not part == '-':
                total += float(Fraction(part))
        quantities[obj['unit']] = {'details': details, 'total': total}
        perIngredient[obj['name']] = quantities

    for name in perIngredient:
        quantities = perIngredient.get(name, {})
        for unit in quantities:
            total = quantities[unit]['total']
            if isInt(total):
                total = int(total)
                if total == 0:
                    total = ''
            else:
                tmp = format(total, '.2f')
                if total < 1:
                    if '.66' in str(total):
                        total = '2/3'
                    elif '.33' in str(total):
                        total = '1/3'
                    else:
                        total = Fraction(total)
                else:
                    total = tmp

            perIngredient[name][unit]['total'] = total
    context['ingredients'] = \
        collections.OrderedDict(sorted(perIngredient.items()))

    return render(request, 'menu.html', context)
