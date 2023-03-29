import {translate as t} from 'corefacility-base/utils';
import UpdateForm from 'corefacility-base/view/UpdateForm';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import CredentialsOutput from 'corefacility-base/shared-view/components/CredentialsOutput';
import AvatarUploader from 'corefacility-base/shared-view/components/AvatarUploader';
import TextareaInput from 'corefacility-base/shared-view/components/TextareaInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import Project from 'corefacility-core/model/entity/Project';
import CoreWindowHeader from 'corefacility-core/view/base/CoreWindowHeader';
import GroupInput from 'corefacility-core/view/group-list/GroupInput';

import style from './style.module.css';


/** This is the base class for all forms that loads existent entity from the
 * 	external source and allow the user to make changes in the entity as well
 * 	as do some extra actions (password change, entity remove etc.)
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
 * 									will be substituted. Such an object must contain
 * 									the 'lookup' button
 * 
 * 		@param {function} on404		The function will be evoked when the server received
 * 									error 404 during the reload or update. We recommend
 * 									you to use this.handle404 when the parent widget is
 * 									an instance of CoreWindow
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
export default class ProjectSettingsForm extends UpdateForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return Project;
	}

	/** Redirection route for "Save and close" and "Close" buttons
	 */
	get entityListRoute(){
		return "/projects/";
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return ['name', 'alias', 'root_group', 'avatar', 'description'];
	}

	/** Renders the form given that the updating entity was successfully loaded.
	 * 		@return {React.Component} Rendered content.
	 */
	renderContent(){
		const PROJECT_NAME_DESCRIPTION = 
			t("The project's name allows to visually distinguish projects between each other");
		const PROJECT_ALIAS_DESCRIPTION = 
			t("Project alias is an unique sequence of digits, latin letters and undescores participates "+
				"to forming the project's URL");
		const PROJECT_ROOT_GROUP_DESCRIPTION = 
			t("All members of this group will also have an access to this project");
		const PROJECT_ICON_DESCRIPTION = t("Put project icon here to visually distinguish projects between each other");

		let formHeader = (this._formObject && this._formObject.name) || t("Project settings");

		return (

			<CoreWindowHeader
				{...this.getMessageBarProps()}
				header={formHeader}
			>
				<Scrollable>
					<form className={`window-form ${style.form}`}>
						<div className={style.base_row}>
							<section className={style.base_settings}>
								<h2>{t("Basic settings")}</h2>
								<Label>{t("Project name") + "*"}</Label>
								<TextInput
									{...this.getFieldProps('name')}
									tooltip={PROJECT_NAME_DESCRIPTION}
									maxLength={64}
								/>
								<Label>{t("Project alias") + "*"}</Label>
								<TextInput
									{...this.getFieldProps('alias')}
									tooltip={PROJECT_ALIAS_DESCRIPTION}
									maxLength={64}
								/>
								<Label>{t("Governing group") + "*"}</Label>
								<GroupInput
									{...this.getFieldProps('root_group')}
									tooltip={PROJECT_ROOT_GROUP_DESCRIPTION}
									groupAddFeature={false}
									mustBeGovernor={!window.application.user.is_superuser}
								/>
								<Label>{t("UNIX group name")}</Label>
								<CredentialsOutput>
									{this._formObject && this._formObject.unix_group}
								</CredentialsOutput>
								<Label>{t("Project directory")}</Label>
								<CredentialsOutput>
									{this._formObject && this._formObject.project_dir}
								</CredentialsOutput>
							</section>
							<section className={style.avatar_settings}>
								<h2>{t("Project Icon")}</h2>
								<AvatarUploader
									{...this.getChildComponentProps('avatar')}
									fileManager={this._formObject && this._formObject.avatar}
									tooltip={PROJECT_ICON_DESCRIPTION}
									width={150}
									height={150}
								/>
							</section>
						</div>
						<section className={style.description_row}>
							<h2>{t("Project description")}</h2>
							<TextareaInput {...this.getFieldProps('description')} maxLength={1024}/>
						</section>
						<div className={style.controls_row}>
							<PrimaryButton {...this.getSubmitProps()}>{t("Save")}</PrimaryButton>
							<PrimaryButton {...this.getSubmitProps()} onClick={this.handleSubmitAndClose}>
								{t("Save and close")}
							</PrimaryButton>
							<PrimaryButton type="cancel" onClick={this.handleClose}>{t("Close")}</PrimaryButton>
						</div>
					</form>
				</Scrollable>
			</CoreWindowHeader>
		);
	}

	componentDidUpdate(prevProps, prevState){
		if (
			this._formObject &&
			!window.application.user.is_superuser &&
			!this._formObject.is_user_governor &&
			this.props.on404){
			this.props.on404();
		} else if (this._formObject &&
			!window.application.user.is_superuser &&
			this._formObject.governor.id !== window.application.user.id &&
			this.props.onNoRootGroup){
			this.props.onNoRootGroup();
		}
	}

}