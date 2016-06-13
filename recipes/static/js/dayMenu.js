/*jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';
import DatePicker from 'react-toolbox/lib/date_picker';
import Dialog from 'react-toolbox/lib/dialog';
import { ThemeProvider } from 'react-css-themr';
import classnames from 'classnames';
import theme from '../css/dayMenu.scss';
import calendarTheme from '../css/calendar.scss';
import dialogTheme from '../css/dialog.scss';

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
    location.href = '/addToMenu/?day=' +
      this.props.date + '&note=' + this.state.selected.id;
  }

  removeRecipe(id) {
    $.ajax({
      url: '/deleteFromMenu/?day=' +
        this.props.date + '&note=' + id
    }).done(function(data) {
      if (data.success) {
        location.reload();
        // this.setState({
        //   recipes: this.state.recipes.filter(recipe => recipe.id != id),
        // });
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
      return <div className={classnames(this.props.theme.row, 'row')} key={'recipe-' + i}>
        <div className={classnames(this.props.theme.col, 'col', 's11')}>
          <a className={classnames(this.props.theme['menu-recipe'])}
            data-position="top"
            data-delay="50"
            data-tooltip="Recipe is missing ingredients!"
            note-id="{recipe.id}"
            key={'recipe-' + recipe.id}
            href={'/note/' + recipe.id}>
            {recipe.title}
          </a>
        </div>
        <div
          onClick={this.removeRecipe.bind(this, recipe.id)}
          className={classnames('col', 's1', this.props.theme['delete-menu-recipe'])}
        >
          <i className={classnames('material-icons', this.props.theme['material-icons'])}>close</i>
        </div>
      </div>;
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

class AggregatedIngredient extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
    };
  }

  onClick() {
    this.setState({expanded: !this.state.expanded});
  }

  render() {
    var quantitiesEls = Object.keys(this.props.quantities).map((unit, j) => {
      return <span key={'quantity-' + j}>
        {' ' + this.props.quantities[unit].total + ' ' + unit}
      </span>;
    });
    var quantityDetails = Object.keys(this.props.quantities).map((unit, j) => {
      var details = this.props.quantities[unit].details.map((q, k) => {
        return <div className={classnames('row')} key={'detail-' + k}>
          <div className={classnames('tooltipped', 'col', 's6')}
            data-position="bottom"
            data-delay="1000"
            data-tooltip="{q.quantity}">
            {q.string}
          </div>
          <div className="col s6">
            <a href={'/note/' + q.note}>
              {q.title}
            </a>
          </div>
        </div>;
      });
      return <div key={'hidden-quantity-' + j}>
        <h5>{this.props.quantities[unit].total + ' ' + unit}</h5>
        {details}
      </div>;
    });
    var detailsClass = this.state.expanded ? '' : 'hidden';
    return <div className={classnames(this.props.theme['menu-ingredient'])}>
      <div onClick={this.onClick.bind(this)}>
        <b>{this.props.name}</b>
        {quantitiesEls}
      </div>
      <div className={detailsClass}>
        {quantityDetails}
      </div>
    </div>;
  }
}

class IngredientsColumn extends React.Component {
  render() {
    if (!this.props.ingredients) {
      return null;
    }
    var ingredients = Object.keys(this.props.ingredients).map((name, i) => {
      return <AggregatedIngredient
        name={name}
        quantities={this.props.ingredients[name]}
        key={'ingredient-' + i}
        theme={this.props.theme}
      />;
    });
    return <div>
      <h5>
        Ingredients
      </h5>
      {ingredients}
    </div>;
  }
}

class Menu extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      week: [],
      ingredients: {},
    };
  }

  componentDidMount() {
    this.serverRequest = $.get(
      this.props.source + location.search,
      function (result) {
        this.setState({
          week: result.week,
          dateFrom: new Date(result.start),
          dateTo: new Date(result.end),
          ingredients: result.ingredients,
        });
      }.bind(this));
  }

  componentWillUnmount() {
    this.serverRequest.abort();
  }

  handleChange(item, value) {
    var formatter = new Intl.DateTimeFormat("en-us", { month: "long" });
    var state = this.state;
    state[item] = value;
    var start =
      state.dateFrom.getDate() +
      '-' +
      formatter.format(state.dateFrom) +
      '-' +
      state.dateFrom.getFullYear();
    var end =
      state.dateTo.getDate() +
      '-' +
      formatter.format(state.dateTo) +
      '-' +
      state.dateTo.getFullYear();
    location.href = '/menu/?start=' + start + '&end=' + end;
  }

  render() {
    if (!this.state.dateFrom || !this.state.dateTo) {
      return null;
    }
    var htmlWeek = this.state.week.map((day, i) => {
      return <MenuDay
          recipes={day.notes || []}
          date={day.date}
          dateString={day.dateString}
          key={'day-' + i}
          theme={this.props.theme}
        />;
    });
    return <div className={classnames(
        this.props.theme.menu,
        'centered',
        'medium',
        'row'
      )} >
      <div className="col s12 m6">
        <h5>
          Days
        </h5>
        <div className={classnames('row')}>
          <div className="col s6">
            <DatePicker
              label="From"
              onChange={this.handleChange.bind(this, 'dateFrom')}
              value={this.state.dateFrom}
              theme={calendarTheme}
            />
          </div>
          <div className="col s6">
            <DatePicker
              label="To"
              onChange={this.handleChange.bind(this, 'dateTo')}
              minDate={this.state.dateFrom}
              value={this.state.dateTo}
              theme={calendarTheme}
            />
          </div>
        </div>
        {htmlWeek}
      </div>
      <div className="col s12 m6">
        <IngredientsColumn
          theme={this.props.theme}
          ingredients={this.state.ingredients}
        />
      </div>
    </div>;
  }
}

ReactDOM.render(
  <Menu source="/getMenu/" theme={theme}/>,
  document.getElementById('dayMenu')
);

module.exports = Menu;
