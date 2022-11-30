import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import DropDown from 'corefacility-base/shared-view/components/DropDown';
import TextInput from 'corefacility-base/shared-view/components/TextInput';

import styles from './style.module.css';


/** Represents the drop down box where the main controlling item is input.
 * 	The drop down box will slide down when the input element is in focus and will slide up when the input element
 * 	blurred.
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
 *	@param {string} tooltip				Detailed description of the field
 * 
 *  @param {string} placeholder			The input placeholder
 * 
 * 	@param {callback} onOpened	 		Triggers when the user opens the drop-down box
 * 
 * 	@param {callback} onClosed			Triggers when the user closes the drop-down box
 * 
 * 	@oaram {boolean} isOpened 			true if the the drop-down is opened, false otherwise. Overrides the isOpened
 * 										state
 * 
 * 	@param {string} inputBoxValue		Current value of the input box when it works in fully controlled mode.
 * 										Overrides the isOpened state.
 * 
 * 	@param {string} inputBoxRawValue	The same as value but before input preprocessing (removing leading and trailing
 * 										whitespaces etc.)
 * ---------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * ---------------------------------------------------------------------------------------------------------------------
 * 	@oaram {boolean} isOpened 			true if the the drop-down is opened, false otherwise.
 * 
 * 	@param {string} inputBoxValue		Current value of the input box.
 * 
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
		if (this.props.onOpened){
			this.props.onOpened(event);
		}
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
		if (this.props.onClosed){
			this.props.onClosed(event);
		}
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

	/** Imperative React: selects a given value, that is:
	 * 	enters this value to the input box
	 * 	closes the drop-down.
	 * 	Triggers the onClosed event.
	 * 
	 * 	@param {string} value 	The value that shall be selected
	 * 	@return {undefined}
	 * 
	 */
	selectValue(value){
		this.setState({
			isOpened: false,
			inputBoxRawValue: value,
			inputBoxValue: value,
		});
		if (this.props.onClosed){
			this.props.onClosed({});
		}
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

	componentDidUpdate(prevProps, prevState){
		if (this.props.isOpened !== undefined && this.state.isOpened !== this.props.isOpened){
			this.setState({isOpened: this.props.isOpened});
		}
		if (this.props.inputBoxRawValue !== undefined && this.state.inputBoxRawValue !== this.props.inputBoxRawValue){
			this.setState({inputBoxRawValue: this.props.inputBoxRawValue});
		}
		if (this.props.inputBoxValue !== undefined && this.state.inputBoxValue !== this.props.inputBoxValue){
			this.setState({inputBoxValue: this.props.inputBoxValue});
		}
	}

}