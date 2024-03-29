import {translate as t} from 'corefacility-base/utils';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import GoogleAuthorizationModule from 'corefacility-core/model/entity/GoogleAuthorizationModule';

import ModuleForm from '../ModuleForm';


/** This is the base class for the Google authorization module form
 * 
 * 	There is following dataflow within the module settings form
 * 
 * 	inputData => defaultValues => rawValues => formValues => formObject => modifyFormObject
 * 
 * 	inputData - a short object that is necessary to build defaultValues.
 * 
 * 	defaultValues - values before the user interactions. These data may
 * 		be downloaded from the external server (in case when user modifies
 * 		the object) or can be simply preliminary set of values (in case
 * 		when user creates new object)
 * 
 * 	rawValues - values entered by the user These values are part of the component
 * 		state: all fields are rendered according to rawValues.
 * 
 * 	formValues - values after primitive proprocessing (i.e., removing loading
 * 		and trailing whitespaces, converting to proper Javascript type, converting
 * 		empty strings to null etc.). These values don't influence on rendering
 * 		of fields.
 * 
 * formObject - strictly must be an instance of Entity.
 * 		On the one hand, formObject is responsible for client-side data validation.
 * 		i.e., it accepts invalidated data from the formValues and must reveal the
 * 		validated data or throw an exception if client-side validation fails.
 * 		On the other side, formObject is the only intermediate that is responsible
 * 		for information exchange between the form and the rest of the world, including
 * 		other components.
 * 
 * 	modifyFormObject - when the formObject is constructedm the modifyFormObject
 * 		becomes the main form function
 * 
 * Props:
 * 		@param {object} options		Auxiliary options to be passed to the form.
 * 									They depend on certain subclass specification.
 * 
 * 		@param {object} inputData	When the prop equals to null or undefined,
 * 									the resetForm() method will not be invoked after
 * 									form mounting or pressing the Reload button from
 * 									the main menu. When the prop equals to object,
 * 									the resetForm() will be invoked during the mount
 * 									or press the reload() button and these input data
 * 									will be substituted.
 * 
 * 		@param {function} on404		The function will be evoked when the server received
 * 									error 404 during the reload or update. We recommend
 * 									you to use this.handle404 when the parent widget is
 * 									an instance of CoreWindow
 * 
 * 		@param {callback} onSettingsBeforeSave triggers before save of the settings
 * 		@param {callback} onSettingsAfterSave  triggers after save of the settings
 * 		@param {callback} onSettingsSaveError  triggers when error occured during the settings save
 * 
 * State:
 * 		@param {object} rawValues	values as they have been entered by the user
 * 
 * 		@param {object} errors 		Field errors. The field error is defined for
 * 			a certain field (e.g., Incorrect e-mail, phone is not filled etc.).
 * 			This state has a form key => value where where key is field name and
 * 			value is error message corresponding to it
 * 
 * 		@param {string} globalError The error unrelated to any of the fields
 * 			(e.g., authentication failed, network disconnected etc.)
 * 
 * 		@param {boolean} inactive	When the form interacts with the server
 * 			(e.g., fetches or posts the data) its interaction with the rest of
 * 			the world is also impossible
 * 
 * 		@param {boolean} canBeActivated true if the module can be activated, false otherwise
 * 
 * 		@param {string} whyCantBeActivated why the module can't be activated?
 * 
 * 		@param {string} additionalNotification An additional error message that shall be placed on the module
 * 											   when the module can be activated and the field value is valid.
 *
 * 		@param {string} redirect	if string, the form will be redirect to the React.js
 * 									route pointed out in this property. If null, no redirection
 * 									will be provided.
 */
export default class GoogleAuthorizationModuleForm extends ModuleForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return GoogleAuthorizationModule;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return ['client_id', 'client_secret'];
	}

	/** Renders all settings for the module widget except Application status -> Enabled checkbox,
	 * 	Save Settings button and 'Settings was not saved' message
	 */
	renderAuxiliarySettings(){
		console.log(this._formObject && this._formObject.toString());

		return [
			<Label>Client ID</Label>,
			<TextInput
				{...this.getFieldProps('client_id')}
				tooltip={t("You must get this feature after registration of your application in the " +
					"Google API Console")}
			/>,
			<Label>Client Secret</Label>,
			<TextInput
				{...this.getFieldProps('client_secret')}
				tooltip={t("You must get this feature after registration of your application in the " +
					"Google API Console")}
			/>,
		];
	}

}