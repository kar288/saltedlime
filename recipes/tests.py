from django.test import TestCase
# from unittest import *
from views import *

class GeneralTests(TestCase):
    # testUrls = [
    #     # 'http://www.bonappetit.com/recipe/colcannon',
    #     # 'http://www.myrecipes.com/recipe/broccoli-casserole-3',
    #     # 'http://www.davidlebovitz.com/2016/02/tangerine-sorbet-ice-cream-recipe/',
    #     # 'http://www.chowhound.com/recipes/slow-cured-corned-beef-31292'
    # ]
    def recipe_general(self, recipe, url):
        fields = ['tags', 'image', 'ingredients', 'instructions', 'title', 'servings']
        for field in fields:
            self.assertIn(field, recipe)
        self.assertGreater(len(recipe['tags']), 0)
        self.assertEquals(recipe['url'], url)

    def test_cookie_and_kate(self):
        url = 'http://cookieandkate.com/2014/feta-fiesta-kale-salad-with-avocado-and-crispy-tortilla-strips/'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], '4')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 14)
        self.assertEquals(recipe['image'], 'http://cookieandkate.com/images/2014/07/feta-fiesta-kale-salad-with-avocado-and-crispy-tortilla-strips.jpg')

    def test_smitten_kitchen(self):
       url = 'http://smittenkitchen.com/blog/2016/03/churros/#more-17497'
       recipe = parseRecipe(url)
       self.recipe_general(recipe, url)
       self.assertEquals(recipe['image'], 'http://smittenkitchen.com/wp-content/uploads/churros.jpg')
       self.assertEquals(recipe['servings'], 'Yield: About 18 6-inch churros')

    def test_food_52(self):
        url = 'http://food52.com/recipes/38513-my-ginger-cookies'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], 'Makes' + u'\xa0' + 'fifty-six 2 1/4-inch cookies')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 14)
        self.assertEquals(recipe['image'], '//images.food52.com/BQivH7Yv0CGwcUaVCkBoc5sdQDs=/753x502/92615718-d956-44f5-99ae-fb261a204340--2015-0915_ginger-molasses-cookies_bobbi-lin_10395.jpg')

    def test_ny_times(self):
        url = 'http://cooking.nytimes.com/recipes/1018037-tamarind-shrimp-with-coconut-milk'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], '4 servings')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 8)
        self.assertIn('/images/2016/03/30/dining/30SPICE3/30SPICE3-superJumbo.jpg', recipe['image'])

    def test_epicurious(self):
        url = 'http://www.epicurious.com/recipes/food/views/strawberry-rhubarb-compote-with-matzo-streusel-topping-109345'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], 'Makes 8 servings')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 12)
        self.assertEquals(recipe['image'], 'http://assets.epicurious.com/photos/56f4270b16f9f5a007cc18ca/1:1/w_600%2Ch_600/EPI_03162016_Strawberry-Rhubarb-Crumble_recipe.jpg')

    def test_the_kitchn(self):
        url = 'http://www.thekitchn.com/recipe-baked-croque-monsieur-casserole-230208'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], 'Serves 8 to 10')
        self.assertEquals(recipe['title'], 'Baked Croque-Monsieur Casserole')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 13)
        self.assertIn('pixstatic.com/570ab88b2a099a2623000f91/_w.1500_s.fit_/TheKitchn_BreakfastCasserole_CroqueMadam02_WEB.jpg', recipe['image'])

    def test_the_kitchn2(self):
        url = 'http://www.thekitchn.com/recipe-ham-and-cheese-breakfas-43364'
        recipe = parseRecipe(url)
        self.recipe_general(recipe, url)
        self.assertEquals(recipe['servings'], 'Serves 6 to 8')
        self.assertEquals(len(recipe['ingredients'].split('\n')), 13)
        self.assertIn('pixstatic.com/56590647dbfa3f2935008d37/_w.1500_s.fit_/Ham-Cheese-Casserole-4884.jpg', recipe['image'])
