import * as React from 'react';

import {NotImplementedError} from '../../exceptions/model.mjs';


/** This is a base class for any button
 *  The button is any widget that executes certain action when
 *  the user clicks on it
 * 
 *  Button props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey
 * 		@param {string} href		the route to be moved when you click the button
 * 	The onClick prop always override the href prop
 */
export default class Button extends React.Component{

	constructor(props){
		super(props);
		this.handleClick = this.handleClick.bind(this);

		if (this.props.disabled && this.props.inactive){
			throw new Error("The button can't be both inactive and disabled");
		}
	}

	/**
	 *  handles the button click.
	 *  When you will decide to extend this base class, pass exactly this callback
	 *  to the callback props, because it accounts for href, disabled and inactive props
	 */
	handleClick(event){
		event.preventDefault();
		if (!this.props.inactive && !this.props.disabled){
			if (this.props.onClick){
				this.props.onClick(event);
			} else if (this.props.href){
				console.log(this.props.href);
			} else {
				console.warning("corefacility.core.view.base.Button: no handler was attached to the button, " +
					"The clicking is useless");
			}
		}
	}

	/** Renders the button. This is an abstract method. So, when you extend the button,
	 *  don't forget to implement this method.
	 *  MIND about conditional rendering because the button may have two states depending
	 *  on the this.props.disabled value: enabled or disabled
	 *  @abstract
	 */
	render(){
		throw new NotImplementedError("render");
		return null;
	}
}