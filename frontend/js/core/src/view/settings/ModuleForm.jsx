import {translate as t} from '../../utils.mjs';
import {NotImplementedError} from '../../exceptions/model.mjs';

import UpdateForm from '../base/UpdateForm.jsx';
import Label from '../base/Label.jsx';
import CheckboxInput from '../base/CheckboxInput.jsx';
import PrimaryButton from '../base/PrimaryButton.jsx';
import styles from './ModuleForm.module.css';


/** This is a base class for all forms that can be used to adjust single module settings.
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
 * 		@param {string} redirect	if string, the form will be redirect to the React.js
 * 									route pointed out in this property. If null, no redirection
 * 									will be provided.
 */
export default class ModuleForm extends UpdateForm{

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		let defaultValues = {};

		this._defaultObject = inputData;
		defaultValues.is_enabled = this._defaultObject.is_enabled;
		for (let field of this.fieldList){
			defaultValues[field] = this._defaultObject[field];
		}

		return defaultValues;
	}

	/** Tells the form what to do if the user presses the 'Submit' buton. It could be
	 * 		posting new entity on the server, requesting for data processing - whenever
	 * 		you want!
	 * 
	 * 	HIGHLY IMPORTANT! Throw an error when the server-side validation fails only!
	 * 	If client-side validation fails, the function must just change and throw
	 * 	ValidationError with no arguments.
	 * 
	 *  @async
	 * 	@return {undefined} all the result is changes in this._formObject
	 * 		The function should throw an exception when server-side validation fails or
	 * 		modify the errors state when the client-side validation fails.
	 */
	async modifyFormObject(){
		if (this.props.onSettingsBeforeSave){
			this.props.onSettingsBeforeSave();
		}
		try{
			await super.modifyFormObject();
			this._formValues.is_enabled = this._formObject.is_enabled;
		} catch (error){
			throw error;
		} finally{
			if (this.props.onSettingsAfterSave){
				this.props.onSettingsAfterSave();
			}
		}
	}

	/**	Transforms Javascript exception to the error message in the message bar.
	 * 
	 * 	@param {Error} error Javascript exception
	 * 	@param {function} tryAgainFunction an optional parameter. If tryAgainFunction is not null or undefined,
	 * 		the user receives "Action required" dialog box and presses Continue, the tryAgainFunction will be executed.
	 * 	@return {string} globalError the global error to lift up the state
	 */
	async handleError(error, tryAgainFunction){
		let globalError = await super.handleError(error, tryAgainFunction);
		if (this.props.onSettingsSaveError){
			this.props.onSettingsSaveError(globalError);
		}
		return globalError;
	}

	/** Renders all settings for the module widget except Application status -> Enabled checkbox,
	 * 	Save Settings button and 'Settings was not saved' message
	 */
	renderAuxiliarySettings(){
		throw new NotImplementedError("renderAuxiliarySettings");
	}

	/** Renders the form given that the updating entity was successfully loaded.
	 * 	@return {React.Component} Rendered content.
	 */
	renderContent(){
		return (
			<form className="settings_form">
				<div className={`widgets_grid ${styles.widgets_grid}`}>
					<Label>{t("Module status")}</Label>
					<CheckboxInput
						{...this.getFieldProps("is_enabled")}
						value={this._formValues && this._formValues.is_enabled}
						label={t("Enabled")}
						tooltip={t("The module doesn't work until this is enabled.")}/>
					{this.renderAuxiliarySettings()}
				</div>
				<div className={`info_grid ${styles.info_grid}`}>
					{this.renderEntityState()}
				</div>
				<div className={`button_grid ${styles.button_grid}`}>
					<PrimaryButton {...this.getSubmitProps()}>
						{t("Save Settings")}
					</PrimaryButton>
				</div>
			</form>
		);
	}

}