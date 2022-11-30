import {NotImplementedError, ValidationError} from 'corefacility-base/exceptions/model';

import Form from './Form';


/** A superclass for all forms that create the entity
 * 	and posts entity data in the external source
 */
export default class CreateForm extends Form{

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
			/* Providing deferred client-side validation */
			let fieldErrors = {}
			for (let name in this._formValues){
				try{
					this._formObject[name] = this._formValues[name];
				} catch (error){
					fieldErrors[name] = error.message;
				}
			}
			/* If client-side validation fails, we need to brake the promise chain */
			if (Object.keys(fieldErrors).length > 0){
				this.setState({
					errors: fieldErrors,
				});
				throw new ValidationError();
			}
		}
		/* Sending data to the server where (a) server-side validation will be provided;
		 *  (b) the entity will be saved to the database or another external source
		 */
		await this._formObject.create();
	}

}