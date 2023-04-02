import {translate as t} from 'corefacility-base/utils';
import {ValidationError} from 'corefacility-base/exceptions/model';
import CreateForm from 'corefacility-base/view/CreateForm';
import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import CheckboxInput from 'corefacility-base/shared-view/components/CheckboxInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import Group from 'corefacility-core/model/entity/Group';
import UserInput from 'corefacility-core/view/user-list/UserInput';

import style from './style.module.css';


/** The group add box. Using this box, the user can provide group name and group governor
 *  for the form create.
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
export default class GroupAddBox extends CreateForm{

	constructor(props){
		super(props);
		this.changeNoGroupLeaderState = this.changeNoGroupLeaderState.bind(this);
		this.changeGroupLeaderId = this.changeGroupLeaderId.bind(this);

		this.state = {
			...this.state,
			noGroupLeader: true,
		}
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return Group;
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@abstract
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		this.setState({noGroupLeader: true});
		return {
			name: null
		}
	}

	/** Renders the component
	 * 	@abstract
	 */
	render(){
		let allowToChangeGovernor = window.application.user.is_superuser;

		return (
			<DialogBox
				{...this.getDialogProps()}
				title={t("Add group")}
			>
				{this.renderSystemMessage()}
				<div className={style.input}>
					<Label>{t("Group name")}</Label>
					<TextInput
						{...this.getFieldProps('name')}
						maxLength={256}
					/>
					{allowToChangeGovernor && <Label>{t("Group leader")}</Label>}
					{allowToChangeGovernor && <div className={style.owner_input}>
						{!this.state.noGroupLeader && <UserInput
							{...this.getFieldProps('governor_id')}
							placeholder={t("Type name of the group leader here...")}
							onItemSelect={this.changeGroupLeaderId}
						/>}
						<CheckboxInput
							label={t("You are the group leader")}
							value={this.state.noGroupLeader}
							onInputChange={this.changeNoGroupLeaderState}
						/>
					</div>}
				</div>
				<div className={style.controls}>
					<PrimaryButton {...this.getSubmitProps()}>{t("Continue")}</PrimaryButton>
					<PrimaryButton
						type="cancel"
						onClick={event => this.dialog.closeDialog(false)}
					>
						{t("Cancel")}
					</PrimaryButton>
				</div>
			</DialogBox>
		);
	}

	/**
	 * Changes whether the group leader information will NOT be sent to the server
	 */
	changeNoGroupLeaderState(event){
		this.setState({noGroupLeader: event.value});
		if (event.value){
			this.setState({
				errors: {
					...this.state.errors,
					governor_id: null,
				}
			});
			this._formValues.governor_id = undefined;
			if (this._formObject !== null){
				this._formObject.governor_id = undefined;
			}
		}
	}

	/**
	 *	Changes the group leader
	 *  @param {User} user 		New leader of the group
	 */
	changeGroupLeaderId(user){
		this.setState({
			errors: {
				...this.state.errors,
				governor_id: null,
			}
		});
		this._formValues.governor_id = user.id;
		if (this._formObject !== null){
			this._formObject.governor_id = user.id;
		}
	}

	/** Tells the form what to do if the user presses the 'Submit' buton. It could be
	 * 		posting new entity on the server, requesting for data processing - whenever
	 * 		you want!
	 * 
	 * 	If the function throws an error, this error become a form's global error.
	 * 	@abstract
	 *  @async
	 * 	@return {undefined} all the result is changes in this._formObject
	 */
	async modifyFormObject(){
		if (!this.state.noGroupLeader && this._formValues.governor_id === undefined){
			this.setState({
				errors: {
					...this.state.errors,
					governor_id: t("Please, specify the group leader")
				}
			});
			throw new ValidationError();
		}
		return await super.modifyFormObject();
	}

}