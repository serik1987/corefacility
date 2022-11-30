import * as React from 'react';
import {Navigate} from 'react-router-dom';

import {NotImplementedError} from 'corefacility-base/exceptions/model';


/** This is a base class for any button
 *  The button is any widget that executes certain action when
 *  the user clicks on it
 * 
 *  Button props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey
 * 	The onClick prop always override the href prop
 * 
 * 	*  The component has internal states.
 */
export default class Button extends React.Component{

	constructor(props){
		super(props);
		this.handleClick = this.handleClick.bind(this);

		if (this.props.disabled && this.props.inactive){
			throw new Error("The button can't be both inactive and disabled");
		}

		this.state = {
			__redirect: false,
		}
	}

	/** The button is considered to be disabled when either its 'disabled' prop is true or:
	 * 	(1) its onClick prop is undefined, (2) its href prop is not undefined, (3) its
	 * 	href prop refers to the current location.
	 */
	get disabled(){
		return this.props.disabled || (
			!this.props.onClick && this.props.href === window.location.pathname
		);
	}

	/**
	 *  handles the button click.
	 *  When you will decide to extend this base class, pass exactly this callback
	 *  to the callback props, because it accounts for href, disabled and inactive props
	 */
	handleClick(event){
		event.preventDefault();
		if (!this.props.inactive && !this.disabled){
			if (this.props.onClick){
				this.props.onClick(event);
			} else if (this.props.href){
				this.setState({
					__redirect: true,
				})
			} else {
				console.warn("corefacility.core.view.base.Button: no handler was attached to the button, " +
					"The clicking is useless");
			}
		}
	}

	render(){
		if (this.state.__redirect){
			return <Navigate to={this.props.href}/>
		} else {
			return this.renderContent();
		}
	}

	/** Renders the button. This is an abstract method. So, when you extend the button,
	 *  don't forget to implement this method.
	 *  MIND about conditional rendering because the button may have two states depending
	 *  on the this.props.disabled value: enabled or disabled.
	 * 
	 * 	Don't override the render() method because such a method is responsible for proper
	 * 	work of href prop.
	 *  @abstract
	 */
	renderContent(){
		throw new NotImplementedError("render");
	}
}
