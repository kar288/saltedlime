/*jshint esversion: 6 */

import calendarFactory from 'react-toolbox/lib/date_picker/Calendar.js';
import Dialog from 'react-toolbox/lib/dialog';
import React from 'react';
import { IconButton } from 'react-toolbox/lib/button';
import ProgressBar from 'react-toolbox/lib/progress_bar';

import addRecipeToMenuModalTheme from '../css/addRecipeToMenuModal.scss';
import calendarTheme from '../css/calendar.scss';
import classnames from 'classnames';
import dialogTheme from '../css/dialog.scss';
import time from 'react-toolbox/lib/utils/time.js';

const Calendar = calendarFactory(IconButton);
class AddRecipeCalendarDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      date: new Date()
    };
    this.actions = [
      { label: 'Cancel', onClick: this.props.onDismiss },
      { label: 'Ok', onClick: this.handleSelect.bind(this) }
    ];
  }

  handleCalendarChange(value, dayClick) {
    const state = {display: 'months', date: value};
    this.setState(state);
  }

  handleSelect(event) {
    if (this.props.done) {
      this.props.onDismiss();
    }
    if (this.props.onSelect) {
      this.props.onSelect(this.state.date, event);
    }
  }

  updateStateDate(date) {
    if (Object.prototype.toString.call(date) === '[object Date]') {
      this.setState({
        date
      });
    }
  }

  render() {
    var theme = this.props.theme;
    var content = (
      <div>
        <h5 className={theme.title}>Add <span className={theme.name}>{this.props.recipe}</span> to your menu on:</h5>
        <div className="row">
          <div className="col s4">
            <header className={classnames(theme.header)}>
              <span className={theme.year}>
                {this.state.date.getFullYear()}
              </span>
              <h3 className={theme.date}>
                {time.getShortDayOfWeek(this.state.date.getDay())}, {time.getShortMonth(this.state.date)} {this.state.date.getDate()}
              </h3>
            </header>
          </div>

          <div className="col s8">
            <div>
              <Calendar
                display={this.state.display}
                onChange={this.handleCalendarChange.bind(this)}
                selectedDate={this.state.date}
                theme={theme} />
            </div>
          </div>
        </div>
      </div>
    );
    if (this.props.pending) {
      content = (
        <div>
          <h4 className={theme.title}>Adding recipe ...</h4>
          <ProgressBar className={theme.progress} type="circular" mode="indeterminate" />
        </div>
      );
    } else if (this.props.done && !this.props.error) {
      content = (
        <div>
          <h4 className={theme.title}>{this.props.message}</h4>
        </div>
      );
    }
    return (
      <Dialog
        active={this.props.active}
        type="custom"
        actions={this.actions}
        theme={theme}
      >
        {content}
      </Dialog>
    );
  }
}

class AddRecipeToMenuModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      pending: false,
    };
  }

  handleToggle() {
    this.setState({active: !this.state.active, done: false, error: false});
  }

  handleSelect(value) {
    var formatter = new Intl.DateTimeFormat("en-us", { month: "long" });
    var date =
      value.getDate() +
      '-' +
      formatter.format(value) +
      '-' +
      value.getFullYear();
    this.setState({pending: true});
    $.ajax({
      url: '/addToMenu/?day=' +
        date + '&note=' + this.props.recipeId
    }).done(function(data) {
      if (data.success) {
        this.setState({
          pending: false,
          done: true,
          error: false,
          message: 'Recipe added!'
        });
      } else {
        this.setState({
          pending: false,
          done: true,
          error: true,
          message: 'An error occurred, please try again!'
        });
      }
    }.bind(this));
  }

  render() {
    return <div
      onClick={this.handleToggle.bind(this)}
      className="default-primary-color card-title add-to-menu"
    >
      Add to day menu
      <AddRecipeCalendarDialog
        active={this.state.active}
        onDismiss={this.handleToggle.bind(this)}
        onSelect={this.handleSelect.bind(this)}
        recipe={this.props.recipeTitle}
        pending={this.state.pending}
        message={this.state.message}
        done={this.state.done}
        error={this.state.error}
        theme={addRecipeToMenuModalTheme}
      />
    </div>;
  }
}


module.exports = AddRecipeToMenuModal;
