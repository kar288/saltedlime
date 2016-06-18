/*jshint esversion: 6 */

import Dialog from 'react-toolbox/lib/dialog';
import React from 'react';
import Tooltip from 'react-toolbox/lib/tooltip';

import classnames from 'classnames';
import dialogTheme from '../css/dialog.scss';
import theme from '../css/dayMenu.scss';


class MenuDay extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      recipes: this.props.recipes,
    };
    this.actions = [
      { label: "Cancel", onClick: this.handleToggle.bind(this) },
      { label: "Submit", onClick: this.submitRecipe.bind(this) },
    ];
  }

  handleToggle() {
    this.setState({active: !this.state.active});
  }

  submitRecipe(e) {
    e.preventDefault();
    if (!this.state.selected) {
      return;
    }
    $.ajax({
      url: '/addToMenu/?day=' +
        this.props.date + '&note=' + this.state.selected.id
    }).done(function(data) {
      if (data.success) {
        this.props.updateRecipes();
        var recipes = this.state.recipes;
        recipes.push(data.note);
        this.setState({
          recipes: recipes,
          active: false,
        });
      }
    }.bind(this));
  }

  removeRecipe(id) {
    $.ajax({
      url: '/deleteFromMenu/?day=' +
        this.props.date + '&note=' + id
    }).done(function(data) {
      if (data.success) {
        this.props.updateRecipes();
        this.setState({
          recipes: this.state.recipes.filter(recipe => recipe.id != id),
        });
      }
    }.bind(this));
  }

  componentDidUpdate() {
    $('.autocomplete').autocomplete({
      serviceUrl: '/note-autocomplete',
      minLength: 2,
      transformResult: function(data) {
        var exist = {};
        $('.menu-recipe').each(function() {
          exist[$(this).attr('note-id')] = true;
        });
        return {
          suggestions: JSON.parse(data).suggestions.filter(function(el) {
            return !exist[el.id];
          })
        };
      },
      onSelect: function(suggestion) {
        this.setState({selected: suggestion});
      }.bind(this)
    }).bind(this);
  }

  render() {
    var recipes = this.state.recipes.map((recipe, i) => {
      return (
        <MenuDayRecipe
          key={'recipe-' + i}
          removeRecipe={this.removeRecipe.bind(this)}
          theme={this.props.theme}
          recipe={recipe}
          tooltip='laaaaaaa'
        />
      );
    });
    return <div className={classnames(this.props.theme.day)}>
        <div className={classnames(this.props.theme.header)}>
          {this.props.dateString}
          <a style={{float: 'right'}} onClick={this.handleToggle.bind(this)} className="waves-effect waves-light">
            <i className="material-icons">add</i>
          </a>
        </div>
        <div className="content">
          {recipes}
        </div>
        <Dialog
          actions={this.actions}
          active={this.state.active}
          onEscKeyDown={this.handleToggle.bind(this)}
          onOverlayClick={this.handleToggle.bind(this)}
          title={'Add recipe to day menu ' + this.props.dateString}
          theme={dialogTheme}
        >
          <form className="ui-widget" onSubmit={this.submitRecipe.bind(this)}>
            <label for={'note-title-' + this.props.date} >Recipe Title: </label>
            <input id={'note-title-' + this.props.date} day="{this.props.date}" className="autocomplete"/>
          </form>
        </Dialog>
      </div>;
  }
}

class MenuDayRecipe extends React.Component {
  render() {
    return <div
      className={classnames(this.props.theme.row, 'row')}
    >
      <div className={classnames(this.props.theme.col, 'col', 's11')}>
        <a className={classnames(
            this.props.theme['menu-recipe'],
            {
              [this.props.theme['no-ingredients']]:
              this.props.recipe.ingredientCount === 0
            }
          )}
          data-position="top"
          data-delay="50"
          data-tooltip="Recipe is missing ingredients!"
          note-id="{recipe.id}"
          key={'recipe-' + this.props.recipe.id}
          href={'/note/' + this.props.recipe.id}>
          {this.props.recipe.title}
        </a>
      </div>
      <div
        onClick={this.props.removeRecipe.bind(this.props.recipe.id)}
        className={classnames('col', 's1', this.props.theme['delete-menu-recipe'])}
      >
        <i className={classnames('material-icons', this.props.theme['material-icons'])}>close</i>
      </div>
    </div>;
  }
}

export default MenuDay;
