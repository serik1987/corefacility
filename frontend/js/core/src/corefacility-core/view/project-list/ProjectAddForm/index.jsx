import {translate as t} from 'corefacility-base/utils';
import CreateForm from 'corefacility-base/view/CreateForm';
import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import Project from 'corefacility-core/model/entity/Project';
import GroupInput from 'corefacility-core/view/group-list/GroupInput';
import Group from 'corefacility-core/model/entity/Group';

import style from './style.module.css';


/** Project add form.
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
export default class ProjectAddForm extends CreateForm{

		/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return Project;
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@abstract
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		return {
			'name': null,
			'alias': null,
			'root_group': null,
		}
	}

	/** Renders the component
	 * 	@abstract
	 */
	render(){
		const PROJECT_NAME_DESCRIPTION =
			t("The project's name allows to visually distinguish projects between each other");
		const PROJECT_ALIAS_DESCRIPTION =
			t("Project alias is an unique sequence of digits, latin letters and undescores " +
			"participates to forming the project's URL");

		return (
			<DialogBox
				{...this.getDialogProps()}
				title={t("Add New Project")}
			>
				{this.renderSystemMessage()}
				<div className={style.data_block}>
					<Label>{t("Project name") + '*'}</Label>
					<TextInput
						{...this.getFieldProps('name')}
						tooltip={PROJECT_NAME_DESCRIPTION}
						maxLength={64}
					/>
					<Label>{t("Project alias") + '*'}</Label>
					<TextInput
						{...this.getFieldProps('alias')}
						tooltip={PROJECT_ALIAS_DESCRIPTION}
						maxLength={64}
					/>
					<Label>{t("Governing group") + '*'}</Label>
					<GroupInput
						{...this.getFieldProps('root_group')}
						tooltip={t("All members of this group will also have an access to this project")}
						mustBeGovernor={!window.application.user.is_superuser}
					/>
				</div>
				<div className={style.control_block}>
					<PrimaryButton {...this.getSubmitProps()}>{t("Continue")}</PrimaryButton>
					<PrimaryButton type="cancel" onClick={event => this.dialog.closeDialog()}>
						{t("Cancel")}
					</PrimaryButton>
				</div>
			</DialogBox>
		);
	}

}
