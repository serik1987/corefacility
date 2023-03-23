import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';

import Label from '../Label';
import TextInput from '../TextInput';
import Icon from '../Icon';

import {ReactComponent as EditIcon} from '../../icons/edit.svg';
import {ReactComponent as ConfirmIcon} from '../../icons/done.svg';
import style from './style.module.css';


/**
 *  Provides a simple label followed by a pencil sign. When the user clicks on the pencil, the label transforms into
 *  the text box. In order to transform the text into the label again, the user shall click on the check sign to
 *  restore the previous view.
 * 
 * 	Props:
 *  --------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 	value			1) If undefined, the widget is stated to be in uncontrolled mode. In this case
 * 										the editing value is defined by the 'value' state.
 * 										1a) The widget is also stated to be in uncontrolled mode when the editMode
 * 										state is true
 * 										2) If defined, the widget is stated to be in controlled mode. In this case
 * 										the editing value is defined by the value of this prop.
 * 	@param {callback}	onInputChange	Triggers when the user changes the value
 * 	@param {string} 	defaultValue	value at widget create. Useless in fully controlled mode.
 * 	@param {string} 	error 			Error message to display
 * 	@param {string}		htmlType		The type="..." attribute for corresponding <input> element
 * 	@param {string}		placeholder 	The text input placeholder
 * 	@param {boolean} 	disabled		When the widget is disabled the user is notified that he can't input the value
 * 	@param {boolean} 	inactive		When the widget is inactive, the user can't change its value
 * 	@param {Number}		maxLength		the input number max length
 * 	@param {string} 	cssSuffix 		Additional CSS classes to apply
 * 
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} 	editMode 		the user can change the input value
 * 	@param {string} 	value 			the value to edit
 */
export default class LabelInput extends React.Component{

	constructor(props){
		super(props);
		this.handleEditIcon = this.handleEditIcon.bind(this);
		this.handleEditBox = this.handleEditBox.bind(this);
		this.confirm = this.confirm.bind(this);

		this.textRef = React.createRef();

		this.state = {
			editMode: false,
			rawValue: null,
			value: null,
		}
		if (this.props.defaultValue !== undefined && this.props.value === undefined){
			this.state.value = this.props.defaultValue;
		}
	}

	/**
	 * Widget's value
	 */
	get value(){
		if (this.props.value === undefined || this.state.editMode){
			return this.state.value;
		} else {
			return this.props.value;
		}
	}

	handleEditIcon(event){
		this.setState({editMode: true, value: this.value});
	}

	handleEditBox(event){
		this.setState({rawValue: event.target.value, value: event.value});
	}

	confirm(event){
		this.setState({editMode: false, rawValue: null});
		if (this.props.onInputChange){
			event.value = this.value;
			this.props.onInputChange(event);
		}
	}

	render(){
		let cssClasses = '';
		if (this.props.cssClasses){
			cssClasses = ` ${this.props.cssClasses}`;
		}

		if (this.state.editMode){
			return (
				<div className={`${style.main} ${style.edit}${cssClasses}`}>
					<TextInput
						value={this.state.rawValue || this.value}
						onInputChange={this.handleEditBox}
						onBlur={this.confirm}
						onEnter={this.confirm}
						ref={this.textRef}
						error={this.props.error}
						htmlType={this.props.htmlType || 'text'}
						placeholder={this.props.placeholder}
						disabled={this.props.disabled || this.props.inactive}
						maxLength={this.props.maxLength}
					/>
					<Icon
						src={<ConfirmIcon/>}
						tooltip={t("Finish edit")}
						onClick={this.confirm}
						disabled={this.props.disabled}
						inactive={this.props.inactive}
					/>
				</div>
			);
		} else {
			return (
				<div className={`${style.main} ${style.no_edit}${cssClasses}`}>
					<Label onClick={this.handleEditIcon}>{this.value}</Label>
					<Icon
						src={<EditIcon/>}
						tooltip={t("Edit this value")}
						onClick={this.handleEditIcon}
						disabled={this.props.disabled}
						inactive={this.props.inactive}
					/>
				</div>
			);
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (this.state.editMode){
			let input = this.textRef.current.domInput;
			if (input !== document.activeElement){
				input.focus();
			}
		}
	}

}