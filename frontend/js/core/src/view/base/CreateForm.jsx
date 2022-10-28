import Form from './Form.jsx';
import {NotImplementedError, ValidationError} from '../../exceptions/model.mjs';


/** A superclass for all forms that create the entity
 * 	and posts entity data in the external source
 */
export default class CreateForm extends Form{

	/** Default values. The form will be reset to these values everytime it opens */
	get defaultValues(){
		throw new NotImplementedError("defaultValues");
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		throw new NotImplementedError("entityClass");
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
		if (shouldUpdate){
			this.setState({
				rawValues: {...this.defaultValues},
				errors: {},
				globalError: null,
			});
		} else {
			this.state = {
				rawValues: {...this.defaultValues},
				errors: {},
				globalError: null,
			}
		}
		this._formValues = {...this.defaultValues};
		this._formObject = null;
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
		if (this._formObject === null){
			this._formObject = new this.entityClass();
			let fieldErrors = {}
			for (let name in this._formValues){
				try{
					this._formObject[name] = this._formValues[name];
				} catch (error){
					fieldErrors[name] = error.message;
				}
			}
			if (Object.keys(fieldErrors).length > 0){
				this.setState({
					errors: fieldErrors,
				});
				throw new ValidationError();
			}
		}
		await this._formObject.create();
	}

}