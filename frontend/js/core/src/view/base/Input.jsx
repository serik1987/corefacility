import {NotImplementedError} from '../../exceptions/model.mjs';
import * as React from 'react';


/** This is the base class for all widgets that accept some text data
 *  entered from the user keyboard
 *  
 *  Props:
 * 		@param {callback} onInputChange		the callback will be executed every time user changes the input
 *                                          the callback function will be invoked with the event argument
 *                                          that contains the 'value' field. This is better to use event.value
 *                                          instead of event.target.value because event.target.value contains
 *                                          row value entered by the user while event.target.value is the value
 *                                          after the following preprocessing:
 *                                           - any whitespaces before and after the value are removed
 *                                           - if the user entered the empty string, the value is null, not ''
 *                                           - you can add additional string preprocessors to this widget
 *                                           - the class descendants may also provide additional preprocessing
 * 
 *		@param {string} value 				Controllable value of the input field. This means that the input value
 *                                          will be set to the value of this prop during each rendering. This results
 *                                          to the following side effects:
 *                                           - If the user entered a value with white spaces, the value is automatically
 *                                             substituted to the value without white spaces.
 *                                           - you obviously need to change the state of the parent component each time
 *                                             the user entered new value. If you will not do this, the component will
 *                                             become useless
 * 
 * 		@param {string} defaultValue		At the first rendering, the input box value will be set to the value
 * 	                                        of this prop. During each next rendering this prop has no effect
 *                                          This prop is overriden by the value prop
 * 
 * 
 *  The input box has the state 'value' which correspond to the value entered by the user but this is not clear
 *  whether you shall trust on this state value or trust the value of the 'value' prop. So, this is recommended
 *  to use the 'value' property rather than the 'value' state.   
 */
export default class Input extends React.Component{

	constructor(props){
		super(props);
		this.onInputChange = this.onInputChange.bind(this);

		this.state = {}
		if (this.props.defaultValue === undefined || this.props.value === null){
			this.state.value = "";
		} else {
			this.state.value = this.props.defaultValue;
		}
	}

	/** The raw value entered by the user (not preprocessed)
	 */
	get value(){
		if (this.props.value === undefined){
			return this.state.value;
		} else if (this.props.value === null){
			return '';
		} else {
			return this.props.value;
		}
	}

	/** Invokes each time the user changes the input
	 *  When you decide to create your own user input, set exactly this callback on the onInputChange property.
	 *  Such callback applies all filters and validators to the entered value, removes leading and trailing whitespaces.
	 *  If the resultant string is empty, the entered value is considered to be null.
	 * 	
	 * 	Also, the method calls props.onInputChange method if the method is presented with the following data passed:
	 * 		@param {string|null} event.value        The value entered by the user before preprocessing
	 *      @param {string}      event.value.target The value entered by the user after preprocessing
	 * 
	 *  When the input field validation fails, the method doesn't call.
	 *  
	 * 		@param {SyntheticEvent} the event triggered by the user. value property will be added to the event.
	 *      @return {undefined}
	 */
	onInputChange(event){
		this.setState({value: event.target.value});
		let value = event.target.value.trim();
		if (value.length === 0){
			value = null;
		}
		if (this.props.onInputChange){
			event.value = value;
			this.props.onInputChange(event);
		}
	}

	/** Renders the input box
	 *  @abstract
	 */
	render(){
		throw new NotImplementedError("render");
		return null;
	}

}