goog.provide('app.recipes.Recipe');

goog.require('app.recipes.RecipeComponent')

app.recipes.Recipe = function(id, url) {
  this.id = id;
  this.url = url;
};

app.recipes.Recipe.prototype.createComponent = function() {
  var recipeElements = goog.dom.getElement('recipes');
  this.component = new app.recipes.RecipeComponent();
  this.component.render(recipeElements);
  this.component.setLabelText(this.url);
};