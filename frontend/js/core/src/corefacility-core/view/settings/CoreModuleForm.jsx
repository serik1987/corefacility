import styled from 'styled-components';

import {translate as t} from 'corefacility-base/utils';
import {DurationManager} from 'corefacility-base/model/fields/DurationField';
import Label from 'corefacility-base/shared-view/components/Label';
import CheckboxInput from 'corefacility-base/shared-view/components/CheckboxInput';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PositiveDurationInput from 'corefacility-base/shared-view/components/PositiveDurationInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import CoreModule from 'corefacility-core/model/entity/CoreModule';

import ModuleForm from './ModuleForm';
import baseStyles from './ModuleForm/style.module.css';


const MaxPasswordSymbols = styled.div`
	display: flex;
	gap: 5px;

	& :last-child{
		width: 75px;
	}
`;

const MaxPasswordSymbolsLabel = styled.div`
	display: inline-block;
	line-height: 32px;
`;

	
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
export default class CoreModuleForm extends ModuleForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return CoreModule;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return [
			"auth_token_lifetime",
			"is_user_can_change_password",
			"max_password_symbols",
		];
	}

	/** Renders the form given that the updating entity was successfully loaded.
	 * 	@return {React.Component} Rendered content.
	 */
	renderContent(){
		return (
			<form className="settings_form">
				<div className={`widgets_grid ${baseStyles.widgets_grid}`}>
					<Label>{t("Session lifetime")}</Label>
					<PositiveDurationInput
						{...this.getFieldProps("auth_token_lifetime")}
						tooltip={t("The user will be automatically logout after this given period of inactivity")}/>
					<Label>{t("User password")}</Label>
					<div>
						<CheckboxInput
							{...this.getFieldProps("is_user_can_change_password")}
							label={t("The user can change his password")}
							tooltip={t("The password change functionality will be appeared above the user profile")}/>
						<MaxPasswordSymbols>
							<MaxPasswordSymbolsLabel>{t("Number of symbols in the password")}</MaxPasswordSymbolsLabel>
							<TextInput
								{...this.getFieldProps("max_password_symbols")}
								tooltip={t("All auto-generated password will have exactly this number of symbols")}
							/>
						</MaxPasswordSymbols>
					</div>
				</div>
				<div className={`info_grid ${baseStyles.info_grid}`}>
					{this.renderEntityState()}
				</div>
				<div className={`button_grid ${baseStyles.button_grid}`}>
					<PrimaryButton {...this.getSubmitProps()}>
						{t("Save Settings")}
					</PrimaryButton>
				</div>
			</form>
		);
	}

}