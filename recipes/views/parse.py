import tldextract
import re
import requests
import traceback
import urllib2

from bs4 import BeautifulSoup, NavigableString
# from BeautifulSoup import BeautifulSoup, NavigableString

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
        html = urllib2.urlopen(req)
    except urllib2.HTTPError, err:
        traceback.print_exc()
        html = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(url)
    #
    # result = requests.get(url)
    # html = result.content
    soup = BeautifulSoup(html, "html.parser")
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

    recipe['title'] = soup.title.string
    title = soup.find(attrs={'property': 'og:title'})
    if title:
        recipe['title'] = title['content']
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
    recipe['title'] = soup.title.string
    title = soup.find('a', attrs={'rel': 'bookmark'})
    if title:
        recipe['title'] = title.text
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
    recipe['title'] = soup.title.string
    title = soup.find(attrs={'property': 'og:title'})
    if title:
        recipe['title'] = title['content']
    recipe['tags'] = getTags(soup, {}, re.compile(r'.*post-categories.*'))
    recipe['image'] = getImage(soup, {"property": "og:image"}, 'content')
    servings = soup.findAll(attrs={'itemprop': 'recipeYield'})
    recipe['servings'] = ' '.join(traverse(servings, ' '))

    ingredientElements = soup.findAll(attrs={'itemprop': 'ingredients'})

    # THIS IS A HACK BUT SOME INGREDIENTS DONT HAVE ITEMPROPS WHILE OTHERS DO
    recipe['ingredients'] = []
    # ingredients = traverse(ingredientElements[0].parent, '\n')
    # for ingredient in ingredients:
    #     recipe['ingredients'] += ingredient.split('\n')

    instructions = []
    ingredients = []

    node = soup.body.find(text=re.compile('^[ ]*(Serves|Yield|Makes)[s]*[: ].*'))
    recipe['servings'] = node
    if not node or node == None:
        return recipe
    while isinstance(node, NavigableString) or not node.name == 'p':
        if node.parent:
            node = node.parent
        else:
            break
    while True:
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if not node or node.name == 'script':
            break

        texts = node.findAll(text=True)
        texts = [i.strip() for i in texts if len(i.strip())]
        if node.find('br') and not node.find('li'):
            ingredients += texts
        else:
            instructions += texts
    if not len(recipe['ingredients']):
        recipe['ingredients'] = ingredients
    recipe['instructions'] = instructions
    return recipe

def parseGeneral(url, soup, recipe):
    if not soup or not soup.title:
        return

    recipe['image'] = getImage(soup)
    ogTitle = soup.find(attrs={'property': 'og:title'})
    if ogTitle:
        recipe['title'] = ogTitle['content']
    else:
        recipe['title'] = soup.title.string

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
