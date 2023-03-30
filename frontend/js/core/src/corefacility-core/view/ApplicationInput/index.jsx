import {translate as t} from 'corefacility-base/utils';
import Module from 'corefacility-base/model/entity/Module';
import SmartEntityInput from 'corefacility-base/view/SmartEntityInput';
import MessageBar from 'corefacility-base/shared-view/components/MessageBar';
import {ReactComponent as Edit} from 'corefacility-base/shared-view/icons/edit.svg';

import style from './style.module.css';


/**
 * 	Allows the user to select certain application from the application list.
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
 * 	@param {Entity} value 					A certain group selected by the user
 * 
 * 	@param {string} rawSearchTerm			Unprocessed search string entered by the user
 * 
 * 	@param {string} searchTerm 				Processed search string entered by the user
 * 
 * 	@param {boolean} isEdit 				true if the widget is in edit state, false otherwise
 */
export default class ApplicationInput extends SmartEntityInput{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return Module;
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let filter = {
			profile: 'light',
			enabled_apps_only: '',
		}
		if (state.searchTerm){
			filter.q = state.searchTerm;
		}
		return filter;
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		let q = '';
		if (state.searchTerm){
			q += state.searchTerm;
		}
		return q;
	}

	/**
	 * 	Renders the widget given that this is in non-edit mode
	 * 	@return {React.Component}
	 */
	renderNonEditMode(){
		let appName = null;
		if (this.value !== null){
			appName = this.value.name;
		} else {
			appName = <i>{t("Choose an application from the list below...")}</i>;
		}

		let mainClasses = style.main;
		if (this.props.inactive){
			mainClasses += ` ${style.inactive}`;
		}
		if (this.props.disabled){
			mainClasses += ` ${style.disabled}`;
		}

		return (
			<div class={mainClasses} onClick={this.handleEditMode}>
				<div className={style.content}>{appName}</div>
				<div className={style.icon}>
					<Edit/>
				</div>
			</div>
		);
	}

	/**
	 * 	Renders content that shows when you open the context menu.
	 */
	renderDropDownContent(){
		let renderMessageBar = this.isLoading || this.isError;

		return (
			<div className={style.dropdown}>
				{renderMessageBar && <MessageBar
					isLoading={this.isLoading}
					isError={this.isError}
					error={this.error}
					isAnimatable={false}
					isInline={true}
				/>}
				<ul>
					{this.itemList && [...this.itemList].map(application => {
						return (
							<li key={application.uuid} onClick={event => this.handleItemSelect(event, application)}>
								{application.name}
							</li>
						);
					})}
				</ul>
			</div>
		);
	}

	/**
	 * 	Triggers when the user shifts to the edit mode
	 * 	@param {SyntheticEvent} event 		The event to trigger
	 */
	handleEditMode(event){
		if (!this.props.inactive && !this.props.disabled){
			super.handleEditMode(event);
		}
	}

	/**
	 *  Triggers when the user selects an application from the application list
	 * 	@param {SyntheticEvent} event 		Event that has triggered this action
	 * 	@param {Module} application 		The application selected by the user
	 */
	handleItemSelect(event, application){
		this.setState({
			value: application,
			isOpened: false,
		});
		if (this.props.onInputChange){
			event.value = event.target.value = application;
			this.props.onInputChange(event);
		}
	}

}