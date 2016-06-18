/*jshint esversion: 6 */

import React from 'react';
import ReactDOM from 'react-dom';

import classnames from 'classnames';
import theme from '../css/dayMenu.scss';

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

export default IngredientsColumn;
