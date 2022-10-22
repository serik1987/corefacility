import EntityField from './field.mjs';
import {ReadOnlyPropertyError} from '../../exceptions/model.mjs';


/** Defines the entity field that can't be modified */
export default class ReadOnlyField extends EntityField{

	/** Creates the entity field that can't be modified
	 *  @param {string} description Human readable description of the field
	 *                  (to be used for debugging purpose only)
	 */
	constructor(description){
		super(undefined, undefined, description, false);
	}

	/** Throws an exception indicating that values of the read-only entity
	 *  fields can't be injected inside the entity
	 */
	proofread(entityName, propertyName, value){
		throw new ReadOnlyPropertyError(entityName, propertyName);
	}

}