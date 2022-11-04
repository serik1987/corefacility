import * as React from 'react';
import Loader from './Loader.jsx'
import {translate as t} from '../../utils.mjs';
import {NotImplementedError} from '../../exceptions/model.mjs';
import * as networkErrors from '../../exceptions/network.mjs';
import styles from '../base-styles/Form.module.css';



/** This is the base abstract class for all web forms.
 * 	The Web forms allow the user to interact with data and change them.
 *  The form manipulate with key => value pairs where key is some short
 *  string to identify certain value and value may have any type.
 * 	Each value is entered by the user in a stand-alone component.
 * 	We will refer to keys as 'field names'.
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
export default class Form extends Loader{

	constructor(props){
		super(props);
		this.handleInputChange = this.handleInputChange.bind(this);
		this.handleSubmit = this.handleSubmit.bind(this);
		this.registerDialog = this.registerDialog.bind(this);
		this._forceUpdate = false; // When this value is true, shouldComponentUpdate is always true
								   // The value becomes false after each form update.
		this.state = {
			rawValues: {},
			errors: {}, 			// Field errors trigger when the user filled the field incorrectly
			noFieldErrors: {},		// No-field errors trigger when the child form element has troubles
			globalError: null,
			inactive: false,
		}
		this._formValues = null;
		this._formObject = null;
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		throw new NotImplementedError("entityClass");
	}

	/** Values after their primitive preprocessing (i.e., removing leading and trailing whitespaces, etc.) */
	get formValues(){
		return this.__formValues;
	}

	/** true if there is at least one field error, false otherwise */
	get hasFieldError(){
		let errors = this.state.errors;
		return  Object.keys(errors).filter(name => errors[name]).length > 0;
	}

	/** true if the form can be submitted (i.e., there are no field errors and global error, all required fields
	 * 	are not empty)
	 */
	get isSubmittable(){
		if (this.hasFieldError){
			return false;
		}

		for (let field in this._formValues){
			if (this.entityClass.isFieldRequired(field) && this._formValues[field] === null){
				return false;
			}
		}

		return true;
	}

	/** If some dialog box is a child component of the form this function must be used as callback ref for
	 * 	this dialog and allow the form to directly control the dialog box.
	 * 
	 * 		@param {DialogBox} the dialog box thatevoked this function
	 * 		@return {undefined}
	 */
	registerDialog(dialog){
		this.dialog = dialog;
		this._isOpened = false;
		this.openDialog = function(inputData){
			this._isOpened = true;
			let openDialogPromise = this.dialog.openDialog(inputData); // First, this.dialog.visible becomes true
			this._forceUpdate = true; // The form should update after its reset, even though the this.dialog.visible
									  // is still false.
			this.resetForm(inputData); // And then, we reset the form
			return openDialogPromise; // In this case, the shouldComponentUpdate is true
		}
	}

	/** Renders props that required for the DialogBox component to be successfully embedded inside the form, including:
	 * 		(1) options - the options prop passed inside the form from the DialogWrapper
	 * 		(2) ref - the registerDialog method that allows the form to achieve direct imerative control on the dialog
	 * 		(3) inactive - correlated with form's inactive state.
	 * 
	 * 	Just do it like here:
	 * 		<DialogBox {...this.getDialogProps()} title="Some Form"/>
	 * 
	 * 	@return {object} set of props that are necessary for dialog to work correctly
	 */
	getDialogProps(){
		return {
			options: this.props.options,
			ref: this.registerDialog,
			inactive: this.state.inactive,
		}
	}

	/** Renders props that required for the MessageBar to be successfully embedded inside the form, including:
	 * 		(1) isLoading - correlated with form's inactive state
	 * 		(2) isError - equals to globalError !== null
	 * 		(3) error - the error to be printed
	 */
	getMessageBarProps(){
		let globalError = this.state.globalError;
		if (!globalError && this.hasFieldError){
			globalError = t("The form was filled incorrectly.");
		}

		return {
			isLoading: this.state.inactive,
			isError: globalError !== null,
			error: globalError,
		}
	}

	/** Renders props of any child component that supply the rawData to the data flow.
	 * 		(i.e., inputs, checkboxes, radiobuttons etc.) - we call them 'fields'
	 * 
	 * The method renders all props that are required for the field to work correctly:
	 * 		(1) value - must be taken from the rawValues object from the form's state
	 * 		(2) error - must be taken from the errors object from the form's state
	 * 		(3) onInputChange - must be form's handleInputChange
	 * 		(4) inactive - must be correlated with the form's inactive state.
	 * 
	 *  Just do it like here:
	 *  <TextInput
	 *				{...this.getFieldProps('surname')}
	 *				htmlType="text"
	 *				tooltip={t("The last name is required for better visualization")}
	 *			/>
	 * 
	 * 
	 * 	@param {string} fieldName	name of the field in the rawValues object
	 * 	@return {object} set of proper props
	 */
	getFieldProps(fieldName){
		return {
			value: this.state.rawValues[fieldName],
			error: this.state.errors[fieldName],
			onInputChange: event => this.handleInputChange(fieldName, event),
			inactive: this.state.inactive,
		}
	}

	/** Renders props of any child component that provide its own interaction with
	 * 	external sources (i.e., file managers, password changers).
	 * 
	 * 	The method will render all props required for correct error displaying:
	 * 		(1) error - must be taken from the errors state
	 * 		(2) onError - will properly set the errors state
	 */
	getChildComponentProps(fieldName){
		return {
			error: this.state.noFieldErrors[fieldName],
			onError: message => this.setChildError(fieldName, message),
		}
	}

	/** Renders props of the submit button.
	 * 
	 * 	The method renders all props that are required for button to work correctly, i.e.,
	 * 		(1) the button type must be "submit"
	 * 		(2) the click handler must be this.handleSubmit
	 * 		(3) the inactive prop must be correlated with the form's inactive state
	 * 		(4) the disabled prop must be correlated with the form's isSubmittable JS property
	 * 
	 *  Just do it like here: <PrimaryButton {...this.getSubmitProps()} >Add</PrimaryButton>
	 */
	getSubmitProps(){
		return {
			type: "submit",
			onClick: this.handleSubmit,
			inactive: this.state.inactive,
			disabled: !this.isSubmittable,
		}
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@abstract
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		throw new NotImplementedError("getDefaultValues");
	}

	/** Reloads the data. This method runs automatically when the componentDidMount.
	 * 	Also, you can invoke it using the imperative React principle
	 * 	@return {undefined}
	 */
	reload(){
		if (this.props.inputData && !this.state.inactive){
			this.resetForm(this.props.inputData);
		}
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
		this.setState({
			errors: {},
			noFieldErrors: {},
			globalError: null,
			inactive: true,
		});
		let defaultValues = await this.getDefaultValues(inputData);
		this.setState({
			rawValues: defaultValues,
			inactive: false,
		});
		this._formValues = defaultValues;
		this._formObject = null;
	}

	/** Tells the form what to do if the user presses the 'Submit' buton. It could be
	 * 		posting new entity on the server, requesting for data processing - whenever
	 * 		you want!
	 * 
	 * 	HIGHLY IMPORTANT! Throw an error when the server-side validation fails only!
	 * 	If client-side validation fails, the function must just change and throw
	 * 	ValidationError with no arguments.
	 * 
	 * 	@abstract
	 *  @async
	 * 	@return {undefined} all the result is changes in this._formObject
	 * 		The function should throw an exception when server-side validation fails or
	 * 		modify the errors state when the client-side validation fails.
	 */
	async modifyFormObject(){
		throw new NotImplementedError("modifyFormObject");
	}

	/** Triggers when the user changes the value in the field.
	 * 
	 * 
	 * 	@param {string} name the field name where user changes the value
	 * 	@param {SyntheticEvent} the event triggered by the object. Because the value
	 * 		preprocessing is made by the field individually, the event must have the
	 * 		following fields:
	 * 			event.target.value - the value before preprocessing (raw value)
	 * 			event.value - the value after preprocessing
	 * 	@return {undefined}
	 */
	handleInputChange(name, event){
		/* First, change rawValues (about rawValues, formValues, formObject see in class description) */
		this.setState({
			rawValues: {
				...this.state.rawValues,
				[name]: event.target.value,
			},
			errors: {
				...this.state.errors,
				[name]: null,
			},
			globalError: null,
		});
		/* Secondly, change formValues */
		if (this._formValues === null){
			throw new TypeError("The Javascript property 'formValues' must be reset in the resetForm() method")
		}
		this._formValues[name] = event.value;
		/* Thirdly, ... */
		if (this._formObject !== null){
			try{
					/* ... change form object or ... */
				this._formObject[name] = event.value;
			} catch (error){
				/* .... print error if client-side validation fails */
				this.setState({
					errors: {						// IMPORTANT! Such operator will work if you guarantee that
						...this.state.errors, 		// you don't change the other field errors previously
						[name]: error.message, 		// In this case we actually did not do that!
					}
				});
			}
		}
	}

	/** Evokes when the user presses the Submit button.
	 * 
	 * 	@param {SyntheticEvent} the event triggered by the submission button
	 * 	@return {boolean} true if the form was successfully submitted, false otherwise
	 */
	async handleSubmit(event){
		let success = false;
		try{
			/* Clear all error messages and lock the form to prevent the user from any consequtive actions */
			this.setState({
				errors: {},
				noFieldErrors: {},
				globalError: null,
				inactive: true,
			});
			/* Change the formObject and call its methods that provide its interaction with the external world */
			await this.modifyFormObject();
			if (this._formObject === null){
				throw new TypeError("The 'modifyFormObject' method should always guarantee that the _formObject is created after promise resolution");
			}
			/* If the dialog box is inside the form, close the dialog box and resolve the dialog box opening promise by the formObject */
			if (this.dialog){
				await this.dialog.closeDialog(this._formObject);
			}
			success = true;
		} catch (error){
			/* In case when the server-side validation fails or  */
			this.handleError(error);
		} finally{
			/* Don't forget to unlock the form in order to allow the user to fix errors or use it again */
			this.setState({inactive: false});
		}
		return success;
	}

	/**	Transforms Javascript exception to the error message in the message bar.
	 * 
	 * 	@param {Error} error Javascript exception
	 * 	@return {undefined}
	 */
	handleError(error){
		if (error instanceof networkErrors.UnauthorizedError){
			/* After application reloading non-authorized users will be moved to the authorization form */
			window.location.reload();
			return;
		}
		
		let fieldErrors = {};
		let globalError = error.message;
		/* When server-side field validation fails, error.info contains information about all invalid fields */
		for (let name in error.info){
			if (name in this._formValues){
				fieldErrors[name] = error.info[name].join(" ");
			}
		}
		/* When server-side field validation fails, the error has no message but has information */
		if (!error.isDetailed && Object.keys(fieldErrors).length > 0){
			globalError = null;
		}
		/* When the object-level validation fails (see https://www.django-rest-framework.org/api-guide/serializers/#object-level-validation)
		 * the error may have no error message, but there are extra information from the error info
		 */
		if (!error.isDetailed && error.info && error.info.non_field_errors){
			globalError = error.info.non_field_errors.join(" ");
		}
		this.setState({
			errors: {...this.state.errors, ...fieldErrors},
			globalError: globalError,
		});
	}

	/** Sets the message to some arbitrary field error. Execution of this function will not result to
	 * 	display of the global error message.
	 * 	This function is suitable for all child components that provide their own network interaction
	 * 	capabilities (i.e., file uploaders, password resets etc.)
	 */
	setChildError(fieldName, message){
		this.setState({
			noFieldErrors: {
				...this.state.noFieldErrors,
				[fieldName]: message,
			}
		});
	}

	shouldComponentUpdate(props, state){
		let shouldUpdate = !this.dialog || this.dialog.visible || this._forceUpdate;
		this._forceUpdate = false; // The _forceUpdate property has just one single effect.
		return shouldUpdate;
	}

	/** Renders the component
	 * 	@abstract
	 */
	render(){
		throw new NotImplementedError("render");
		return null;
	}

	/** Renders special bar containing loading indicator and global error message
	 * 	You should include invocation of this method to your render function if you don't implement
	 * 	message bar.
	 */
	renderSystemMessage(){
		let globalError = this.state.globalError;
		if (!globalError && this.hasFieldError){
			globalError = t("The form was filled incorrectly.");
		}

		return (
			<div className={styles.service_wrapper}>
				{ this.state.inactive && <div className={styles.loading_bar_wrapper}><div className={styles.loading_bar}></div></div> }
				{ globalError !== null && <p className={styles.error_message}>{globalError}</p> }
			</div>
		);
	}

}