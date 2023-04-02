import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {NotImplementedError} from 'corefacility-base/exceptions/model';
import LoadableDropDownInput from 'corefacility-base/shared-view/components/LoadableDropDownInput';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';

import ListLoader from '../ListLoader';
import style from './style.module.css';


/**
 * 	This is an improved widget that allows to pick up certain entity from the entity list. The widget has facilitated
 * 	interaction with forms, better user experience and ability to embed more features. However, this requires
 * 	more development.
 * 
 * 	Generally, use EntityInput when you develop administrator or seldomly used functionality and this one in the rest
 * 	of the cases.
 * 
 * 	Component props:
 * 	--------------------------------------------------------------------------------------------------------------------
 *	@param {callback} onInputChange			The function invoked each time when the user selects a given widget,
 * 											discards any previous selection or chooses to select another widget.
 * 
 *	@param {Entity} value 					When this value is set, the widget is stated to be in parent-controlled
 * 											mode, which means that any user selection will not be applied until they
 * 											are approved by the parent.
 * 
 *	@param {string} defaultValue			At the first rendering, the input box value will be set to the value
 * 	                                        of this prop. During each next rendering this prop has no effect
 *                                          This prop is overriden by the value prop
 * 
 *	@param {string} error 					The error message that will be printed when validation fails
 * 
 *	@param {string} tooltip					Detailed description of the field
 * 
 *  @param {string} placeholder		        The placeholder to output
 * 
 *	@param {boolean} disabled				When the input box is disabled, it is colored as disabled and the user can't
 * 											enter any value to it
 * 									
 * 	@param {boolean} inactive				When the input box is inactive, the user can't enter value to it
 * 
 *  @param {String} cssSuffix   	        Additional CSS classes to apply
 * 
 * 
 * 	Component state:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Entity} value 					A certain entity selected by the user
 * 
 * 	@param {string} rawSearchTerm			Unprocessed search string entered by the user
 * 
 * 	@param {string} searchTerm 				Processed search string entered by the user
 * 
 * 	@param {boolean} isEdit 				true if the widget is in edit state, false otherwise
 */
export default class SmartEntityInput extends ListLoader{

	constructor(props){
		super(props);
		this.handleEditMode = this.handleEditMode.bind(this);
		this.handleSearchChange = this.handleSearchChange.bind(this);
		this.handleDropDownOpen = this.handleDropDownOpen.bind(this);
		this.handleDropDownClose = this.handleDropDownClose.bind(this);
		this.handleTransitionEnd = this.handleTransitionEnd.bind(this);
		this.__dropDown = React.createRef();

		this.state = {
			...this.state,
			value: this.props.defaultValue || null,
			rawSearchTerm: null,
			searchTerm: null,
			isEdit: false,
			isOpened: false,
		}
	}

	/**
	 *  Returns the drop-down input box (for direct React)
	 */
	get dropDown(){
		if (this.state.isEdit === false){
			throw new Error("Can't access this property when the widget is in non-edit mode.");
		}
		return this.__dropDown.current;
	}

	/**
	 *  The widget's value derived from props or state
	 */
	get value(){
		if (this.props.value === undefined){
			return this.state.value;
		} else {
			return this.props.value;
		}
	}

	/**
	 * 	Seeks for the entities in the external Web server.
	 * 	@async
	 */
	async reload(){
		if (this.state.isEdit){
			await super.reload();
		}
	}

	/**
	 * Renders the widget given that this is in non-edit mode
	 * @return {React.Component}
	 */
	renderNonEditMode(){
		throw new NotImplementedError('renderNonEditMode');
	}

	/**
	 * 	Renders content that shows when you open the context menu.
	 */
	renderDropDownContent(){
		throw new NotImplementedError('renderDropDownContent');
	}

	render(){
		let basicWidget = null;

		if (this.state.isEdit){
			basicWidget = (
				<div className={style.edit_mode}>
					<LoadableDropDownInput
						inactive={this.props.inactive}
						disabled={this.props.disabled}
						placeholder={this.props.placeholder}
						isOpened={this.state.isOpened}
						inputBoxRawValue={this.state.rawSearchTerm}
						inputBoxValue={this.state.searchTerm}
						onOpened={this.handleDropDownOpen}
						onClosed={this.handleDropDownClose}
						onTransitionEnd={this.handleTransitionEnd}
						onInputChange={this.handleSearchChange}
						ref={this.__dropDown}
					>
						{this.renderDropDownContent()}
					</LoadableDropDownInput>
					<Icon
						onClick={this.handleDropDownClose}
						inactive={this.props.inactive}
						disabled={this.props.disabled}
						tooltip={t("Cancel")}
						src={<EditIcon/>}
					/>
				</div>
			);
		} else {
			basicWidget = this.renderNonEditMode();
		}

		return (
			<div title={this.props.tooltip} className={this.props.cssSuffix}>
				{basicWidget}
				{this.props.error && <p className={style.error_box}>{this.props.error}</p>}
			</div>
		);
	}

	componentDidUpdate(prevProps, prevState){
		super.componentDidUpdate(prevProps, prevState);
		if (!prevState.isEdit && this.state.isEdit){
			this.dropDown.domInput.focus();
		}
	}

	/**
	 *  Triggers when the user switches to the edit mode.
	 * 	@param {SyntheticEvent} event the event that triggers this action
	 */
	handleEditMode(event){
		this.setState({
			isEdit: true,
			rawSearchTerm: '',
			searchTerm: null,
		});
	}

	/**
	 *  Triggers when the user tries to open the drop down
	 * 	@param {SyntheticEvent} event the event that triggers this action
	 */
	handleDropDownOpen(event){
		this.setState({isOpened: true});
	}

	/**
	 *  Triggers when the search term changes
	 * 	@param {SyntheticEvent} the DOM control that triggered this event
	 */
	handleSearchChange(event){
		this.setState({
			rawSearchTerm: event.target.value,
			searchTerm: event.value,
		});
	}

	/**
	 *  Triggers when the user closes the drop down
	 * 	@param {SyntheticEvent} event the event that triggers this action
	 */
	handleDropDownClose(event){
		this.setState({isOpened: false});
	}

	/**
	 * 	Triggers when the drop down transition event totally closes
	 * 
	 * 	@param {Event|object} information about event that triggered this action. The object contains the following
	 * 	properties:
	 * 		target an HTML element that triggers this transition
	 * 		type an event type or 'timeout' if no TransitionEnd event has been triggered
	 * 		
	 */
	handleTransitionEnd(event){
		this.setState({isEdit: false});
	}

}