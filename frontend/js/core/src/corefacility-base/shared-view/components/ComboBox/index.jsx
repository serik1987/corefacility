import * as React from 'react';

import {ReactComponent as Icon} from 'corefacility-base/shared-view/icons/dropdown_simple.svg';

import DropDownMenu from '../DropDownMenu';
import style from './style.module.css';


/**
 * 	The combo box allows the user to select the value from the predefined list.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {array of object} valueList			List of all available values. The list must be presented in a form of
 * 												Javascript array each item of which is an object with the following
 * 												fields:
 * 		@param {any} value 	 					Value to be returned to the child component.
 * 		@param {string} text					Human-readable value description
 * 
 * 	@param {callback} onInputChange				Triggers when the the user selects another value.
 * 
 * 	@param {any} value 							When this prop is set, the widget is stated to be in parent-controlled
 * 												mode. In this case this prop defines the selected value. Any value
 * 												change made by the user will not take an effect until the parent
 * 												component changes this prop.
 * 												When this prop is undefined, the widget is stated in user-controlled
 * 												mode. In this case, the user can freely change value of this widget but
 * 												its value is inaccessible from the parent.
 * 
 * 	@param {any} defaultValue					Value at the widget construction. Takes no effect in parent-controlled
 * 												mode.
 * 
 * 	@param {string} error 						Widget's error
 * 
 * 	@param {string} tooltip 					A short text to show when the user hover a mouse above this widget
 * 
 * 	@param {boolean} disabled 					The user can't change value of this widget and see this
 * 
 * 	@param {boolean} inactive 					The user can't change value of this widget and can't see this
 * 
 * 	@param {string} cssSuffix 					Additional CSS classes to be applied to the widget's HTML root.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {any} value 							Value selected by the user
 */
export default class ComboBox extends React.Component{

	constructor(props){
		super(props);

		this.state = {
			value: this.props.defaultValue ?? null,
		}
	}

	/**
	 *  Final value that has widget.
	 */
	get value(){
		if (this.props.value === undefined){
			return this.state.value;
		} else {
			return this.props.value;
		}
	}

	/**
	 *  Returns text description of the value
	 */
	get valueText(){
		for (let suggestedValueInfo of this.valueList){
			if (suggestedValueInfo.value === this.value){
				return suggestedValueInfo.text;
			}
		}
		return '';
	}

	/**
	 *  List of all available values
	 */
	get valueList(){
		if (!this.props.valueList){
			throw new Error("the valueList prop is mandatory for the ComboBox component");
		}

		return this.props.valueList;
	}

	/**
	 * 	Renders the combo box caption
	 * 	@return {React.Component}
	 */
	renderCaption(){
		return (
			<div className={style.caption}>
				<div className={style.title}>{this.valueText}</div>
				<div className={style.button}>
					<Icon/>
				</div>
			</div>
		);
	}

	/**
	 *  Renders the item
	 * 	@param {any} value 				the widget's value that will be set when the user clicks on the widget
	 * 	@param {string} text 			human-readable value description
	 * 	@param {boolean} isCurrent		this item has been selected by the user
	 */
	renderItem(value, text, isCurrent){
		let classes = style.item;
		if (isCurrent){
			classes += ` active`;
		}

		return <p className={classes} onClick={event => this.handleItemSelect(event, value)}>{text}</p>;
	}

	render(){
		let mainStyles = style.main;
		if (this.props.inactive){
			mainStyles += ` ${style.inactive}`;
		}
		if (this.props.disabled){
			mainStyles += ` ${style.disabled}`;
		}
		if (this.props.cssSuffix){
			mainStyles += ` ${this.props.cssSuffix}`;
		}

		return (
			<div className={mainStyles} title={this.props.tooltip}>
				<DropDownMenu
					caption={this.renderCaption()}
					items={this.valueList.map(
						item => this.renderItem(item.value, item.text, item.value === this.value)
					)}
					inactive={this.props.inactive || this.props.disabled}
				/>
				{this.props.error && <p className={style.error}>{this.props.error}</p>}
			</div>
		);
	}

	handleItemSelect(event, value){
		if (value === this.value){
			return;
		}
		this.setState({value: value});
		if (this.props.onInputChange){
			event.value = event.target.value = value;
			this.props.onInputChange(event);
		}
	}

}