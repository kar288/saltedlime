/*jshint esversion: 6 */

import AddRecipeToMenuModal from './addRecipeToMenuModal.js'
import Menu from './Menu.js';
import React from 'react';
import ReactDOM from 'react-dom';

import theme from '../css/dayMenu.scss';

var dayMenu = document.getElementById('dayMenu');
if (dayMenu) {
  ReactDOM.render(
    <Menu source="/getMenu/" theme={theme}/>,
    dayMenu
  );
}

var recipeCards = document.getElementsByClassName('recipe-card');
NodeList.prototype.forEach = HTMLCollection.prototype.forEach = Array.prototype.forEach;
recipeCards.forEach(el => {
  ReactDOM.render(
    <AddRecipeToMenuModal recipeTitle={$(el).find('.title').text()} recipeId={el.getAttribute('note-id')} />,
    $(el).find('.add-recipe')[0]
  );
});
