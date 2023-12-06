import {Navigate} from 'react-router-dom';
import styled from 'styled-components';

import {translate as t} from 'corefacility-base/utils';
import EntityState from 'corefacility-base/model/entity/EntityState';
import {NotImplementedError} from  'corefacility-base/exceptions/model';
import {BadRequestError, UnauthorizedError, NotFoundError} from 'corefacility-base/exceptions/network';

import Form from './Form';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import {ReactComponent as ExclamationMark} from 'corefacility-base/shared-view/icons/error.svg';


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
export default class UpdateForm extends Form{

	showDeletedObject = true;

	constructor(props){
		super(props);
		this.handleClose = this.handleClose.bind(this);
		this.handleSubmitAndClose = this.handleSubmitAndClose.bind(this);
		this.handleDelete = this.handleDelete.bind(this);

		this.state = {
			...this.state,
			redirect: null,
		}
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		throw new NotImplementedError('get fieldList');
	}

	/** Redirection route for "Save and close" and "Close" buttons
	 */
	get entityListRoute(){
		throw new NotImplementedError("get entityListRoute");
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		let defaultValues = {};
		this.setState({
			"reloadError": this.__reloadError = null,
		});
		try{
			if (!('lookup' in inputData)){
				throw new Error("UpdateForm.getDefaultValues: bad entity lookup");
			}
			this._defaultObject = await this.fetchObject(inputData.lookup);
			for (let field of this.fieldList){
				defaultValues[field] = this._defaultObject[field];
			}
			this.setState({
				"reloadError": this.__reloadError = null,
			});
		} catch (error){
			for (let field of this.fieldList){
				defaultValues[field] = null;
			}
			this.setState({
				"reloadError": this.__reloadError = error,
			});
		}
		return defaultValues;
	}

	/**
	 *  Requests the object from the server
	 * 	@async
	 * 	@param {Any} 	lookup 			The object identity (e,g., ID, alias, ...)
	 * 	@return the object itself
	 */
	async fetchObject(lookup){
		return await this.entityClass.get(lookup);
	}

	/** Sets default values to the form. The function calls everywhere when the dialog box opens
	 * 	or the form initializes.
	 * 	@async
	 * 	@abstract
	 * 	@param {any} inputData some input data depending on the subclass
	 * 	@param {shouldUpdate} true to update the state, false to initialize new state.
	 * 	@return {undefined}
	 * 
	 */
	async resetForm(inputData){
		if (this._formObject && this._formObject.state === EntityState.deleted){
			return;
		}
		await super.resetForm(inputData);
		if (this._defaultObject){
			this._formObject = this._defaultObject;
		}
		if (this.__reloadError){
			this._formValues = {};
			this._formObject = null;
			this.setState({
				globalError: this.__reloadError.message,
				inactive: false,
			});
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
		await this._formObject.update();
		let updatedValues = {};
		for (let field of this.fieldList){
			updatedValues[field] = this._defaultObject[field];
		}
		this.setState({
			rawValues: updatedValues,
		})
		this._formValues = {...updatedValues};
	}

	/** Handles press on the "Close" button that has to show the list
	 * 	of all form objects.
	 */
	handleClose(event){
		if (this.dialog !== null && this.dialog !== undefined){
			throw new Error("The closing feature doesn't work on dialog boxes. Use this.dialog.closeDialog(false) instead");
		}
		this.setState({redirect: this.entityListRoute});
	}

	/** Handles press on the "Save and close" button that has to save the formObject
	 * 	and show the list of all form objects.
	 */
	async handleSubmitAndClose(event){
		let submissionResult = await this.handleSubmit(event);
		if (submissionResult){
			this.handleClose(event);
		}
	}

	/** Handles press on the "Remove" button that has to delete the _formObject
	 * 	from all external service
	 */
	async handleDelete(event){
		let self = this;
		let userWantsToDelete = await this.promptDelete(event);
		if (!userWantsToDelete){
			return false;
		}
		return await (async function tryAgainFunction(force = false){
			let result = false;
			try{
				self.setState({
					errors: {},
					globalError: null,
					inactive: true,
				});
				if (force){
					await self._formObject.forceDelete();
				} else {
					await self._formObject.delete();
				}
				result = true;
			} catch (error){
				self.handleError(error, tryAgainFunction);
			} finally {
				self.setState({inactive: false});
			}
			return result;
		})();
	}

	/** Asks the user whether he wants to delete the form object
	 */
	async promptDelete(event){
		return await window.application.openModal("question", {
			caption: t("Delete confirmation"),
			prompt: t("Do you really want to delete this resource?"),
		});
	}

	/** Renders the form given that the updating entity was successfully loaded.
	 * 		@return {React.Component} Rendered content.
	 */
	renderContent(){
		throw new NotImplementedError("renderContent");
	}

	/** Renders "Data have not been saved!" bar
	 */
	renderEntityState(){
		let Warning = styled.p`
			margin: 0;
			color: rgb(197, 57, 41);
			fill: rgb(197, 57, 41);

			${Warning} svg{
				display: inline-block;
				vertical-align: middle;
				margin-right: 10px;
				width: 24px;
				height: 24px;
			}
		`;

		if (this._formObject && this._formObject.state === EntityState.changed){
			return (
				<Warning>
					<ExclamationMark/>
					{t("The data have not been saved!")}
				</Warning>
			);
		}
	}

	render(){
		let ErrorMessage = styled.p`
			padding: 15px 30px 15px 115px;
		`;

		let ErrorElement = styled.span`
			color:  rgb(197, 57, 41);
		`;

		if (this.state.redirect !== null){
			return <Navigate to={this.state.redirect}/>;
		}

		if (this._formObject && this._formObject.state === EntityState.deleted && this.showDeletedObject){
			return (
				<ErrorMessage className="already-deleted">
					<i>{t("The requested resource has already been deleted.")}</i>
					{" "}
					<Hyperlink href={this.entityListRoute}>
						{t("Go back...")}
					</Hyperlink>
				</ErrorMessage>
			);
		}

		if (!this.state.reloadError){
			return this.renderContent();
		}

		if (this.state.reloadError instanceof UnauthorizedError){
			window.parent.location.reload();
		}

		if (this.state.reloadError instanceof NotFoundError && this.props.on404){
			this.props.on404();
		}

		return (
			<ErrorMessage className="epic-fail">
				<ErrorElement>{this.state.reloadError.message}</ErrorElement>
				{" "}
				<Hyperlink onClick={ event => this.reload() }>
					{t("Try again.")}
				</Hyperlink>
			</ErrorMessage>
		);
	}

}