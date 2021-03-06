# -*- coding: utf-8 -*-

# import html5lib
import re
import traceback
import unicodedata
import urllib2
from fractions import Fraction

import requests
import tldextract
from bs4 import BeautifulSoup, NavigableString
from pattern.en import singularize

from recipes.models import Ingredient, Month, Note, Recipe, RecipeUser
from utils import *

vulgarFractions = {
    u'↉': '0',
    u'⅟': '1',
    u'⅒': '1/10',
    u'½': '1/2',
    u'⅓': '1/3',
    u'¼': '1/4',
    u'⅕': '1/5',
    u'⅙': '1/5',
    u'⅐': '1/7',
    u'⅛': '1/8',
    u'⅑': '1/9',
    u'⅔': '2/3',
    u'⅖': '2/5',
    u'¾': '3/4',
    u'⅗': '3/5',
    u'⅜': '3/8',
    u'⅘': '4/5',
    u'⅚': '5/6',
    u'⅝': '5/8',
    u'⅞': '7/8',
}

def isInt(s):
    try:
        return s == int(s)
    except ValueError:
        return False

def getQuantity(s):
    try:
        number = float(s)
        return s
    except ValueError:
        pass

    try:
        import unicodedata
        number = unicodedata.numeric(s)
        return ' ' + str(vulgarFractions.get(s, ''))
    except (TypeError, ValueError):
        pass

    try:
        number = float(Fraction(s))
        return s
    except ValueError:
        pass

    if len(s) == 1:
        return ''

    tmp = ''
    for c in s:
        q = getQuantity(c)
        if not q:
            return ''
        else:
            tmp += q

    return tmp

basicUnits = ['ml', 'l', 'g']

def is_unit(s):
    units = {
        'pinch': True,
        'tablespoon': True,
        'teaspoon': True,
        'tbsp': True,
        'tbsps': True,
        'tsp': True,
        'tsps': True,
        'cup': True,
        'pound': True,
        'oz': True,
        'ounces': True,
        'liter': True,
        'millilitre': True,
        'millilitres': True,
        'grams': True,
        'head': True,
        'bunch': True,
        'ml': True,
        'l': True,
        'g': True,
    }
    return s in units

def is_descriptor(s):
    descriptors = {
        'large': True,
        'small': True,
        'scant': True,
        'medium': True,
        'heaping': True,
        'peeled': True,
        'to': True,
        'overripe': True,
    }
    return s in descriptors

def normalizeUnit(unit):
    if not len(unit):
        return unit

    unit = unit.split('/')[0]
    substitutions = [
        {'name': 'teaspoon', 'sub': 'tsp'},
        {'name': 'tablespoon', 'sub': 'tbsp'},
        {'name': 'ounce', 'sub': 'oz'},
        {'name': 'pound', 'sub': 'lb'},
        {'name': 'millilitre', 'sub': 'ml'},
        {'name': 'litre', 'sub': 'l'},
        {'name': 'kilogram', 'sub': 'kg'},
        {'name': 'gram', 'sub': 'g'},
    ]
    if unit[-1] == 's':
        unit = unit[:-1]
    for substitution in substitutions:
        if substitution['name'] in unit:
            return unit.replace(substitution['name'], substitution['sub'])
    return unit

def getNGrams(size, parts):
    if size == 1:
        return parts
    bigrams = []
    for i in range(len(parts) - size + 1):
        bigrams.append(' '.join(parts[i : i + size]))
    return bigrams

def getIngredientName(ingredient):
    ingredient = ingredient.replace('  ', ' ').replace(",", "").lower()
    ingredient = re.sub(r' \([^)]*\)', '', ingredient)
    parts = ingredient.strip().split(' ')
    for i in range(3, 0, -1):
        ngrams = getNGrams(i, parts)
        for part in ngrams:
            clean = part.strip()
            if not 'our' in clean:
                clean = singularize(clean)
            if 'spoon' in clean or 'cup' in clean:
                continue
            ingredients = Ingredient.objects.filter(name = clean)
            if not len(ingredients):
                continue
            p = ingredient.split(part)
            if not len(p):
                return {
                    'name': ingredients[0].name,
                    'quantity': '',
                    'unit': ''
                }
            unit = ''
            quantity = ''
            numbersDone = False
            tokens = p[0].split()
            if not tokens:
                continue
            tmp = tokens[0]
            # 25ml, 8g ...
            if len(tmp) and getQuantity(tmp[0]):
                for basicUnit in basicUnits:
                    if basicUnit in tmp:
                        tmp = tmp.replace(basicUnit, ' ' + basicUnit)
                        tokens = tmp.split() + tokens[1:]
                        break

            for token in tokens:
                if is_unit(token) and not is_descriptor(token):
                    numbersDone = True
                    unit = token
                    break
                if not numbersDone:
                    tmpQuantity = getQuantity(token)
                    if tmpQuantity:
                        quantity += tmpQuantity + ' '
                    elif token == '-':
                        quantity = ''
                    else:
                        if len(quantity):
                            numbersDone = True
                            if not is_descriptor(token):
                                unit = token
                                break
            unit = normalizeUnit(unit)
            if not quantity:
                quantity = ''
            return {
                'name': ingredients[0].name,
                'quantity': quantity,
                'unit': unit
            }
    return {}

def getImage(soup, attr=None, key=None):
    imageUrl = ''
    attrs = [attr] if attr is not None else [
        {"property": "og:image"},
        {"name": "twitter:image:src"},
        {"itemprop": "image"},
        {"rel": "image_src"}
    ]
    keys = [key] if key is not None else [
        'content',
        'src',
        'href'
    ]
    for attr in attrs:
        image = soup.find(attrs=attr)
        if image:
            for key in keys:
                if image.has_attr(key):
                    imageUrl = image[key]
                    break
        if imageUrl:
            break
    if not imageUrl:
        images = soup.findAll('img')
        if len(images) and images[0] and images[0].has_attr('src'):
            imageUrl = images[0]['src']

    return imageUrl

def getTags(soup, attr=None, link=None):
    tagsResult = []
    tagAttrs = [
        {'itemprop': 'keywords'},
        {'itemprop': 'recipeCategory'},
        {'name': 'keywords'},
        {'property': 'article:tag'},
        {'name': 'sailthru.tags'},
        {'name': 'parsely-tags'}
    ]
    if attr is not None and attr:
        tagAttrs = [attr]
    tagLinks = []
    if link is None:
        tagLinks = [
            'tags-nutrition-container',
            re.compile(r'.*post-categories.*'),
            re.compile(r'.*postmetadata.*')
        ]
    elif link:
        tagLinks = [link]

    tagContainer = None
    for tagLink in tagLinks:
        tagContainer = soup.findAll(attrs={'class': tagLink})
        if tagContainer:
            break

    if tagContainer and len(tagContainer):
        tags = tagContainer[0].findAll('a')
        tagVals = [tag.text.lower().replace(' ', '-') for tag in tags]
        tagsResult = tagVals

    for tagAttr in tagAttrs:
        tags = soup.findAll(attrs=tagAttr)
        tagsArray = [tag['content'] for tag in tags if tag and tag.has_attr('content')]
        if len(tags) and not len(tagsArray):
            tagsArray = traverse(tags, '')
        if len(tagsArray) == 1 and ',' in tagsArray[0]:
            tagsArray = tagsArray[0].split(',')
        tagsArray = [tag.strip().lower() for tag in tagsArray]
        tagsResult += tagsArray

    return list(set(tagsResult))

def getTitle(soup, tag=None, attr=None):
    title = soup.title
    if not title:
        return ''
    result = soup.title.string
    titleTag = soup.find(tag, attrs=attr)
    if titleTag:
        if 'content' in titleTag and titleTag['content']:
            result = titleTag['content']
        elif titleTag.text:
            result = titleTag.text
    return result

def traverse(nodes, separator):
    texts = []
    for node in nodes:
        parts = []
        for part in node.findAll(text=True):
            stripped = part.strip()
            if len(stripped):
                parts.append(stripped)
        texts.append(separator.join(parts))
    return texts
    # return '\n'.join(texts)

def parseRecipe(url):
    if not url.startswith('http'):
        url = 'http://' + url
    recipe = {'url': url}
    try:
        req = urllib2.Request(url.encode("utf8"), headers={'accept': '*/*', 'User-Agent' : "Magic Browser"})
        html = urllib2.urlopen(req, timeout=10)
        charset = html.headers.getparam('charset')
        if not charset:
            charset = 'utf-8'
        html = html.read().decode(charset)
    except urllib2.HTTPError, err:
        traceback.print_exc()
        logger.error(url + ' - error in parsing httperror')
        html = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(url)

    soup = BeautifulSoup(html, "html5lib")
    if 'nyt' in url:
        parseNYT(soup, recipe)
    elif 'food52' in url:
        parseFood52(soup, recipe)
    elif 'epicurious' in url:
        parseEpicurious(soup, recipe)
    elif 'davidlebovitz' in url:
        parseDavidLebovitz(soup, recipe)
    elif 'myrecipes' in url:
        parseMyRecipes(soup, recipe)
    elif 'bonappetit' in url:
        parseBonAppetit(soup, recipe)
    elif 'chowhound' in url:
        parseChowhound(soup, recipe)
    elif 'smittenkitchen' in url:
        parseSmittenKitchen(soup, recipe)
    elif 'thekitchn' in url:
        parseTheKitchn(soup, recipe)
    elif 'cookieandkate' in url:
        parseCookieAndKate(soup, recipe)
    elif 'foodnetwork' in url:
        parseFoodNetwork(soup, recipe)
    else:
        parseGeneral(url, soup, recipe)
    recipe['instructions'] = '\n'.join(recipe.get('instructions', []))
    recipe['ingredients'] = '\n'.join(recipe.get('ingredients', []))
    return recipe

def parserTemplate(soup, recipe, tagAttr, tagLink, ingredientAttr,\
    image={"property": "og:image"}, imageKey='content'):

    recipe['title'] = getTitle(soup, 'meta', {'property': 'og:title'})
    recipe['tags'] = getTags(soup, tagAttr, tagLink)
    instructionElements = soup.findAll(attrs={'itemprop': 'recipeInstructions'})
    recipe['instructions'] = traverse(instructionElements, '\n')
    ingredientElements = soup.findAll(attrs={'itemprop': ingredientAttr})
    recipe['ingredients'] = traverse(ingredientElements, ' ')
    recipe['image'] = getImage(soup, image, imageKey)
    servings = soup.find(attrs={'itemprop': 'recipeYield'})
    if servings:
        if servings.has_attr('content'):
            recipe['servings'] = servings['content']
        else:
            recipe['servings'] = servings.text
        recipe['servings'] = recipe['servings'].strip()
    else:
        recipe['servings'] = ''
    return recipe


def parseNYT(soup, recipe):
    recipe =  parserTemplate(soup, recipe,
        {},
        'tags-nutrition-container',
        'recipeIngredient'
    )
    return recipe

def parseBonAppetit(soup, recipe):
    return parserTemplate(soup, recipe,
        {'property': 'article:tag'},
        '',
        'ingredients'
    )

def parseChowhound(soup, recipe):
    return parserTemplate(soup, recipe,
        {},
        re.compile(r'.*freyja_tagslist.*'),
        'ingredients'
    )

def parseEpicurious(soup, recipe):
    return parserTemplate(soup, recipe,
        {'itemprop': 'keywords'},
        '',
        'ingredients'
    )

def parseFood52(soup, recipe):
    recipe = parserTemplate(soup, recipe,
        {'name': 'sailthru.tags'},
        '',
        'ingredients',
        {'itemprop': 'image'},
        'src'
    )
    return recipe

def parseMyRecipes(soup, recipe):
    return parserTemplate(soup, recipe,
        {'name': 'keywords'},
        '',
        'recipeIngredient'
    )

def parseDavidLebovitz(soup, recipe):
    return parserTemplate(soup, recipe,
        {'property': 'article:tag'},
        '',
        'recipeIngredient'
    )

def parseCookieAndKate(soup, recipe):
    return parserTemplate(soup, recipe,
        {},
        'entry-categories',
        'ingredients'
    )

def parseFoodNetwork(soup, recipe):
    recipe = parserTemplate(soup, recipe,
        {'itemprop': 'recipeCategory'},
        '',
        'ingredients'
    )
    if len(recipe['instructions']):
        instructions = recipe['instructions'][0]
        if 'CATEGORIES' in instructions:
            instructions = instructions.split('CATEGORIES')[0]
        recipe['instructions'] = [instructions]
    return recipe

def parseSmittenKitchen(soup, recipe):
    recipe['title'] = getTitle(soup, 'a', {'rel': 'bookmark'})
    recipe['tags'] = getTags(soup, {}, re.compile(r'.*postmetadata.*'))
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    instructions = []
    ingredients = []
    recipe['ingredients'] = ingredients
    recipe['instructions'] = instructions

    servings = soup.find(text=re.compile('^(Serves|Yields|Makes|Yield).*'))
    if not servings:
        return recipe
    node = servings.parent
    recipe['servings'] = ' '.join(node.findAll(text=True)).strip()
    while True:
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if not node or node.name == 'script':
            break

        texts = node.findAll(text=True)
        texts = [i.strip() for i in texts]
        if node.find('br'):
            ingredients += texts
        else:
            instructions += texts
    recipe['ingredients'] = ingredients
    recipe['instructions'] = instructions
    return recipe

def parseTheKitchn(soup, recipe):
    recipe['title'] = getTitle(soup, '', {'itemprop': 'name'})
    recipe['tags'] = getTags(soup, {}, re.compile(r'.*post-categories.*'))
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    recipe['servings'] = ' '.join(traverse(servings, ' '))
    ingredients = soup.findAll(attrs={'itemprop': 'ingredients'})
    ingredientContainer = None
    if len(ingredients):
        ingredientContainer = ingredients[0].parent
        recipe['ingredients'] = traverse([ingredientContainer], '\n')
    if not ingredientContainer:
        instruction = None
    else:
        instruction = ingredientContainer.nextSibling

    instructions = []
    while instruction:
        if not isinstance(instruction, NavigableString):
            instructions.append('\n'.join(traverse([instruction], '\n')))
        instruction = instruction.nextSibling
    recipe['instructions'] = instructions
    return recipe

def parseGeneral(url, soup, recipe):
    if not soup:
        return

    recipe['image'] = getImage(soup)
    recipe['title'] = getTitle(soup, 'meta', {'property': 'og:title'})

    instructionElements = soup.findAll(attrs={'itemprop': 'recipeInstructions'})
    recipe['instructions'] = traverse(instructionElements, '\n')
    recipe['tags'] = getTags(soup)
    ingredientElements = soup.findAll(attrs={'itemprop': 'recipeIngredient'})
    if not len(ingredientElements):
        ingredientElements = soup.findAll(attrs={'itemprop': 'ingredients'})
    recipe['ingredients'] = traverse(ingredientElements, ' ')

    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    if len(servings) and servings[0].has_attr('content'):
        recipe['servings'] = servings[0]['content']
    else:
        recipe['servings'] = ' '.join(traverse(servings, ' '))

    return recipe
