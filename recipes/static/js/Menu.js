/*jshint esversion: 6 */

import DatePicker from 'react-toolbox/lib/date_picker';
import IngredientsColumn from './IngredientsColumn.js';
import React from 'react';
import MenuDay from './MenuDay.js';

import calendarTheme from '../css/calendar.scss';
import classnames from 'classnames';

class Menu extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      week: [],
      ingredients: {},
    };
  }

  updateRecipes() {
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

  componentDidMount() {
    this.updateRecipes();
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
          updateRecipes={this.updateRecipes.bind(this)}
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

module.exports = Menu;
