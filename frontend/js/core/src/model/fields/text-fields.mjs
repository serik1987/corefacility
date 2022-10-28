import {translation as t} from '../../utils.mjs';
import {ValidationError} from '../../exceptions/model.mjs';
import Field from './field.mjs';


/** Validates aliases, logins etc.
 */
export default class SlugField extends Field{

	pattern = /^[-a-zA-Z0-9_]+$/;

	/** Moves the field value from the entity user to the internal entity state
	 *  @param {string} entityName name of the entity which value is intended to be saved
	 *  @param {string} propertyName  field name
	 *  @param {any} value the field value given by the entity user
	 *  @return {any} the value to be stored in the entity
	 */
	proofread(entityName, propertyName, value){
		let internalValue = super.proofread(entityName, propertyName, value);
		return internalValue;
	}

}