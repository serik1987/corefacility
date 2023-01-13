import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import Form from 'corefacility-base/view/Form';
import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import style from './style.module.css';


/** A form that shall be used for the authorization settings
 * 
 * 	Such data have the following flow:
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
 * 
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
 */
export default class AuthorizationSettingsForm extends Form{

	constructor(props){
		super(props);
		this.handleClose = this.handleClose.bind(this);
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return null;
	}

	/** URL to retrieve / post settings
	 */
	get settingsUrl(){
		let clientVersion = window.SETTINGS.client_version;
		return `/api/${clientVersion}/users/${this._userId}/authorizations/${this._moduleAlias}/`;
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@async
	 * 	@param {object} inputData some input data passed to the form (They could be undefined)
	 * 	@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		let defaultValues = {};
		if (!this._isOpened){
			return {};
		}

		try{
			let {userId, moduleAlias, moduleName} = inputData;
			this._userId = userId;
			this._moduleAlias = moduleAlias;
			this._moduleName = moduleName
			this._formValues = {};
			let {values, description} = await client.get(this.settingsUrl);
			defaultValues = values;
			this._description = description;
		} catch (error){
			this.handleError(error, () => this.getDefaultValues(inputData));
		}
		return defaultValues;
	}

	handleClose(event){
		if (this.dialog){
			this.dialog.closeDialog();
		}
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
		let result = await client.post(this.settingsUrl, this._formValues);
		this._formObject = result;
	}

	/** Renders the component
	 */
	render(){
		let title;
		if (this._moduleName){
			title = this._moduleName;
		} else {
			title = t("Authorization Method Setup");
		}

		return (
			<DialogBox {...this.getDialogProps()} title={title}>
				{this.renderSystemMessage()}
				<div className={style.settings_wrapper}>
					{Object.keys(this.state.rawValues).map(fieldName => {
						return [
							<Label>{this._description.email}</Label>,
							<TextInput
								{...this.getFieldProps(fieldName)}
							/>
						];
					})}
				</div>
				<div className={style.controls_wrapper}>
					<PrimaryButton {...this.getSubmitProps()}>{t("Continue")}</PrimaryButton>
					<PrimaryButton type='cancel' inactive={this.state.inactive} onClick={this.handleClose}>
						{t("Cancel")}
					</PrimaryButton>
				</div>
			</DialogBox>
		);
	}

}