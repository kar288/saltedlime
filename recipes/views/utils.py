from django.db.models.functions import Lower
from recipes.models import RecipeUser

def getUser(user):
    recipeUser = RecipeUser.objects.filter(googleUser = user) | RecipeUser.objects.filter(facebookUser = user)
    if not recipeUser.exists():
        raise Http404("No such user.")
    return recipeUser[0]
