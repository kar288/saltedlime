from django.db.models.functions import Lower
from django.http import JsonResponse, Http404
from recipes.models import RecipeUser

import logging

logger = logging.getLogger('recipesParsing')

def normalizeURL(url):
    if not url[-1] == '/':
        return url + '/'
    return url

def getUser(user):
    recipeUser = RecipeUser.objects.filter(googleUser = user) | RecipeUser.objects.filter(facebookUser = user)
    if not recipeUser.exists():
        raise Http404("No such user.")
    return recipeUser[0]


def recipeUser(request):
    if request.user.is_anonymous():
        return {}
    recipeUser = getUser(request.user)
    return { 'profile_pic': recipeUser.profilePic }
