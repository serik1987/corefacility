import * as React from 'react';
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
 * 	defaultValues => rawValues => formValues => formObject => modifyFormObject
 * 
 * 	defaultValues - values before the user interactions. These data may
 * 		be downloaded from the external server (in case when user modifies
 * 		the object) or can be simply preliminary set of values (in case
 * 		when user creates new object)
 * 
 * 	rawValues - values entered by the user
 * 
 * 	formValues - values after primitive proprocessing (i.e., removing loading
 * 		and trailing whitespaces, converting to proper Javascript type, converting
 * 		empty strings to null etc.)
 * 
 * formObject - on the one hand, formObject is responsible for client-side data validation.
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
 * Props:
 * 		@param {object} options		Auxiliary options to be passed to the form.
 * 									They depend on certain subclass specification.
 * 
 * State:
 * 		@param {object} rawValues	values as they have been entered by the user
 * 		@param {object} errors 		Field errors. The field error is defined for
 * 			a certain field (e.g., Incorrect e-mail, phone is not filled etc.).
 * 			This state has a form key => value where where key is field name and
 * 			value is error message corresponding to it
 * 		@param {string} globalError The error unrelated to any of the fields
 * 			(e.g., authentication failed, network disconnected etc.)
 * 		@param {boolean} inactive	When the form interacts with the server
 * 			(e.g., fetches or posts the data) its interaction with the rest of
 * 			the world is also impossible
 */
export default class Form extends React.Component{

	constructor(props){
		super(props);
		this.handleInputChange = this.handleInputChange.bind(this);
		this.handleSubmit = this.handleSubmit.bind(this);
		this.registerDialog = this.registerDialog.bind(this);
		this._forceUpdate = false; // When this value is true, shouldComponentUpdate is always true
								   // The value becomes false after each form update.
		this.state = {
			rawValues: null,
			errors: {},
			globalError: null,
			inactive: false,
		}
		this._formValues = null;
		this._formObject = null;
		this.resetForm(null, false);
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

	/** Renders props of the child DialogBox. Must be used in the render function like here:
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

	/** Renders props of any child component that supply the rawData to the data flow.
	 * 		(i.e., inputs, checkboxes, radiobuttons etc.)
	 * 
	 *  You need to set these props if you want your form to work correctly, like here...
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

	/** Sets default values to the form. The function calls everywhere when the dialog box opens
	 * 	or the form initializes.
	 * 	@async
	 * 	@abstract
	 * 	@param {any} inputData some input data depending on the subclass
	 * 	@param {shouldUpdate} true to update the state, false to initialize new state.
	 * 	@return {undefined}
	 * 
	 */
	async resetForm(inputData, shouldUpdate = true){
		throw new NotImplementedError("resetForm");
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
		throw new NotImplementedError("modifyFormObject");
	}

	/** Triggers when the user changes the value in the field.
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

		if (this._formValues === null){
			throw new TypeError("The Javascript property 'formValues' must be reset in the resetForm() method")
		}
		this._formValues[name] = event.value;
		if (this._formObject !== null){
			this.fillFormObject(name, event.value);
		}
	}

	/** Sets proper value to the form field.
	 *  Throws an exception if the value is invalid
	 * 
	 * 	@param {string} name the field name
	 * 	@param {string} value the field value from the formValues
	 * 	@return {boolean} true if the form is valid, false otherwise
	 */
	fillFormObject(name, value){
		try{
			this._formObject[name] = value;
			return true;
		} catch (error){
			this.setState({
				errors: {
					...this.state.errors,
					[name]: error.message,
				}
			});
			return false;
		}
	}

	/** Evokes when the user presses the Submit button.
	 * 
	 * 	@param {SyntheticEvent} the event triggered by the submission button
	 * 	@return {undefined}
	 */
	async handleSubmit(event){
		try{
			this.setState({
				errors: {},
				globalError: null,
				inactive: true,
			});
			await this.modifyFormObject();
			if (this._formObject === null){
				throw new TypeError("The 'modifyFormObject' method should always guarantee that the _formObject is created after promise resolution");
			}
			if (this.dialog){
				await this.dialog.closeDialog(this._formObject);
			}
		} catch (error){
			this.handleError(error);
		} finally{
			this.setState({inactive: false});
		}
	}

	/**	Transforms Javascript exception to the error message in the message bar
	 * 
	 * 	@param {Error} error Javascript exception
	 * 	@return {undefined}
	 */
	handleError(error){
		switch (error.constructor){
			case networkErrors.UnauthorizedError:
				window.location.reload();
				break;
			default:
				let fieldErrors = {};
				let globalError = error.message;
				for (let name in error.info){
					if (name in this._formValues){
						fieldErrors[name] = error.info[name].join(" ");
					}
				}
				if (!error.isDetailed && Object.keys(fieldErrors).length > 0){
					globalError = null;
				}
				if (!error.isDetailed && error.info && error.info.non_field_errors){
					globalError = error.info.non_field_errors.join(" ");
				}
				this.setState({
					errors: {...this.state.errors, ...fieldErrors},
					globalError: globalError,
				});
		}
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
	 * 	You must include invocation of this method to your render function
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