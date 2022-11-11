import * as React from 'react';

import {NotImplementedError} from '../../exceptions/model.mjs';
import DropDown from './DropDown.jsx';
import TextInput from './TextInput.jsx';
import styles from '../base-styles/DropDownInput.module.css';


/** Represents the drop down box where the main controlling item is input.
 * 	The drop down box will slide down when the input element is in focus and will slide up when the input element
 * 	blurred.
 * 
 * 	All components of this class can work in fully uncontrolled mode only. However, any subclass may define its
 * 	own fully controlled mode.
 * 
 * 	The drop down input is stated to work in fully uncontrolled mode if its value widget is fully defined by the
 * 	widget's internal state. The parent component doesn't have to do anything but this is unable to set up the value.
 * 
 * 	Props:
 * ---------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} inactive			if true, the input box will be inactive and hence will not expand or contract
 *	 									the item box.
 *	@param {boolean} disabled			When the input box is disabled, it is colored as disabled and the user can't
 * 										enter any value to it
 * 
 *	@param {string} error				The error message that will be printed when validation fails
 * 
 *	@param {string} htmlType			Type of the HTML's input element. For list of available types see here:
 * 											https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types
 * 										The following types are supported: email, password, search, tel, text, url
 * 
 *	@param {string} tooltip				Detailed description of the field
 * 
 *  @param {string} placeholder			The input placeholder
 * ---------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * ---------------------------------------------------------------------------------------------------------------------
 * 	@param {string} inputBoxValue		Current value of the input box when it works in fully uncontrolled mode.
 * 										Useless when it works in fully controlled mode.
 * 	@param {string} inputBoxRawValue	The same as value but before input preprocessing (removing leading and trailing
 * 										whitespaces etc.)
 * ---------------------------------------------------------------------------------------------------------------------
 */
export default class DropDownInput extends React.Component{

	constructor(props){
		super(props);
		this.handleInputChange = this.handleInputChange.bind(this);
		this.handleFocus = this.handleFocus.bind(this);
		this.handleMenuClose = this.handleMenuClose.bind(this);

		this.state = {
			isOpened: false,
			inputBoxRawValue: null,
			inputBoxValue: null,
		}
	}

	/** Value of the input box as it will be printed inside the input box
	 */
	get inputBoxRawValue(){
		return this.state.inputBoxRawValue;
	}

	/** Value of the input box as it will be sent to the parent component.
	 */
	get inputBoxValue(){
		return this.state.inputBoxValue;
	}

	/** Handles focus on the input element. (The drop down must be opened.)
	 * 
	 * 	@param {SyntheticEvent} the event that has been triggered the focus
	 */
	handleFocus(event){
		this.setState({isOpened: true});
	}

	/** Handles blur from the input element. (Does nothing but subclasses must redefine it.)
	 */
	handleBlur(event){

	}

	/** Handles click outside the window (The drop down must be closed.)
	 * 
	 *  @param {SyntheticEvent} the event that has been triggered on menu close
	 */
	handleMenuClose(event){
		this.setState({isOpened: false});
	}

	/** Handles the input change of the box. (The state must be changed.)
	 * 	To be re-defined in subclasses
	 * 
	 * 	@param {SyntheticEvent} the event that has been triggered
	 */
	handleInputChange(event){
		this.setState({
			inputBoxRawValue: event.target.value,
			inputBoxValue: event.value,
		});
	}

	/** Renders children inside the drop down
	 */
	renderChildren(){
		throw new NotImplementedError("renderChildren");
	}

	render(){
		return (
			<DropDown
				isOpened={this.state.isOpened}
				onMenuClose={this.handleMenuClose}
				cssSuffix={styles.drop_down}
				caption={
					<TextInput
						onInputChange={this.handleInputChange}
						onFocus={this.handleFocus}
						onBlur={this.handleBlur}
						inactive={this.props.inactive}
						disabled={this.props.disabled}
						value={this.inputBoxRawValue}
						error={this.props.error}
						tooltip={this.props.tooltip}
						placeholder={this.props.placeholder}
					/>
				}
				>
					{this.renderChildren()}
			</DropDown>
		);
	}

}