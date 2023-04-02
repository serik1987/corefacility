import {translate as t} from 'corefacility-base/utils';

import CoreWindow from 'corefacility-core/view/base/CoreWindow';
import AuthorizationSettingsForm from 'corefacility-core/view/user-list/AuthorizationSettingsForm';
import ProfileForm from './ProfileForm';


/**
 * A window that the user can use to adjust its settings
 */
export default class ProfileWindow extends CoreWindow{

	constructor(props){
		super(props);
		this.handleNameChange = this.handleNameChange.bind(this);
		this.handleAuthorizationSetup = this.handleAuthorizationSetup.bind(this);
		this.registerModal('authorization-method-setup', AuthorizationSettingsForm);
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Profile");
	}

	/** Renders the area on the top of the Web browser window;
	 *  between the logo and the controls
	 *  @abstract
	 * 	@return {React.js component}
	 */
	renderControls(){
		return null;
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<ProfileForm
				inputData={{}}
				ref={this.setReloadCallback}
				onNameChange={this.handleNameChange}
				onAuthorizationMethodSetup={this.handleAuthorizationSetup}
			/>
		);
	}

	/**
	 * Triggers when the user changes its name or surname
	 */
	handleNameChange(newName){
		this._setBrowserTitle(newName);
	}

	/**
	 * Triggers when the user clicks on a given authorization method
	 * @async
	 * @param {ModuleWidget} authorizationWidget the authorization module selected by the user
	 */
	async handleAuthorizationSetup(authorizationWidget){
		return await this.openModal('authorization-method-setup', {
			userId: window.application.user.id,
			moduleAlias: authorizationWidget.alias,
			moduleName: authorizationWidget.name,
		});
	}

}