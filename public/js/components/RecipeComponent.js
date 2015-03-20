goog.provide('app.recipes');
goog.provide('app.recipes.RecipeComponent');

goog.require('goog.dom');
goog.require('goog.dom.classlist');
goog.require('goog.events.EventType');
goog.require('goog.events.KeyCodes');
goog.require('goog.events.KeyHandler');
goog.require('goog.ui.Component');



/**
 * A simple box that changes colour when clicked. This class demonstrates the
 * goog.ui.Component API, and is keyboard accessible, as per
 * http://wiki/Main/ClosureKeyboardAccessible
 *
 * @param {string=} opt_label A label to display. Defaults to "Click Me" if none
 *     provided.
 * @param {goog.dom.DomHelper=} opt_domHelper DOM helper to use.
 *
 * @extends {goog.ui.Component}
 * @constructor
 * @final
 */
app.recipes.RecipeComponent = function(opt_label, opt_domHelper) {
  goog.base(this, opt_domHelper);

  /**
   * The label to display.
   * @type {string}
   * @private
   */
  this.initialLabel_ = opt_label || 'Click Me';

  /**
   * The current color.
   * @type {string}
   * @private
   */
  this.color_ = 'red';

  /**
   * Keyboard handler for this object. This object is created once the
   * component's DOM element is known.
   *
   * @type {goog.events.KeyHandler?}
   * @private
   */
  this.kh_ = null;
};
goog.inherits(app.recipes.RecipeComponent, goog.ui.Component);


/**
 * Changes the color of the element.
 * @private
 */
app.recipes.RecipeComponent.prototype.changeColor_ = function() {
  if (this.color_ == 'red') {
    this.color_ = 'green';
  } else if (this.color_ == 'green') {
    this.color_ = 'blue';
  } else {
    this.color_ = 'red';
  }
  this.getElement().style.backgroundColor = this.color_;
};


/**
 * Creates an initial DOM representation for the component.
 * @override
 */
app.recipes.RecipeComponent.prototype.createDom = function() {
  this.decorateInternal(this.dom_.createElement('div'));
};


/**
 * Decorates an existing HTML DIV element as a SampleComponent.
 *
 * @param {Element} element The DIV element to decorate. The element's
 *    text, if any will be used as the component's label.
 * @override
 */
app.recipes.RecipeComponent.prototype.decorateInternal = function(element) {
  goog.base(this, 'decorateInternal', element);
  if (!this.getLabelText()) {
    this.setContent(this.initialLabel_);
  }

  var elem = this.getElement();
  goog.dom.classlist.add(elem, goog.getCssName('recipe-component'));
};


/** @override */
app.recipes.RecipeComponent.prototype.disposeInternal = function() {
  goog.base(this, 'disposeInternal');
  if (this.kh_) {
    this.kh_.dispose();
  }
};


/**
 * Called when component's element is known to be in the document.
 * @override
 */
app.recipes.RecipeComponent.prototype.enterDocument = function() {
  goog.base(this, 'enterDocument');
  this.getHandler().listen(this.getElement(), goog.events.EventType.CLICK,
      this.onDivClicked_);
};


/**
 * Called when component's element is known to have been removed from the
 * document.
 * @override
 */
app.recipes.RecipeComponent.prototype.exitDocument = function() {
  goog.base(this, 'exitDocument');
};


/**
 * Gets the current label text.
 *
 * @return {string} The current text set into the label, or empty string if
 *     none set.
 */
app.recipes.RecipeComponent.prototype.getLabelText = function() {
  if (!this.getElement()) {
    return '';
  }
  return goog.dom.getTextContent(this.getElement());
};


/**
 * Handles DIV element clicks, causing the DIV's colour to change.
 * @param {goog.events.Event} event The click event.
 * @private
 */
app.recipes.RecipeComponent.prototype.onDivClicked_ = function(event) {
  this.changeColor_();
};


/**
 * Fired when user presses a key while the DIV has focus. If the user presses
 * space or enter, the color will be changed.
 * @param {goog.events.Event} event The key event.
 * @private
 */
app.recipes.RecipeComponent.prototype.onKey_ = function(event) {
  var keyCodes = goog.events.KeyCodes;
  if (event.keyCode == keyCodes.SPACE || event.keyCode == keyCodes.ENTER) {
    this.changeColor_();
  }
};


/**
 * Sets the current label text. Has no effect if component is not rendered.
 *
 * @param {string} text The text to set as the label.
 */
app.recipes.RecipeComponent.prototype.setContent = function(text, imageUrl) {
  if (this.getElement()) {
    goog.dom.setTextContent(this.getElement(), text);
  }

  var image = goog.dom.createElement('img');
  image.src = imageUrl;
  image.style.width = '30px';
  this.getElement().appendChild(image);
};
