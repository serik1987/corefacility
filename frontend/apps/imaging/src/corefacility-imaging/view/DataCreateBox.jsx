import CreateForm from 'corefacility-base/view/CreateForm';

import FunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import MapFormFields from './MapFormFields';


/**
 * 	Allows the user to create new functional map object on the server.
 * 
 * 	Functional map data have the following flow:
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
export default class DataCreateBox extends CreateForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return FunctionalMap;
	}

	/**
     *  Creates new entity with the state 'creating'
     *  @return {Entity} entity to create
     */
    createEntity(){
        return new FunctionalMap({}, window.application.project)
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
			'alias': null,
			'type': 'ori',
			'width': 12400,
			'height': 12400,
		}
	}

	/** Renders the component
	 * 	@abstract
	 */
	render(){
		return (
			<MapFormFields
				dialogBoxOptions={this.getDialogProps()}
				messageBar={this.renderSystemMessage()}
				aliasFieldOptions={this.getFieldProps('alias')}
				typeFieldOptions={this.getFieldProps('type')}
				widthFieldOptions={this.getFieldProps('width')}
				heightFieldOptions={this.getFieldProps('height')}
				submitProps={this.getSubmitProps()}
				cancelProps={{
					onClick: event => this.dialog.closeDialog(false),
					inactive: this.state.inactive,
				}}
			/>
		);
	}

}