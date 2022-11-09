import EntityState from '../entity/entity-state.mjs';
import {ReadOnlyField} from './fields.mjs';


/** The field represents a valid object and allows
 * 	to access any properties of this object.
 * 
 * 	The object is in FOUND state which means that this is
 * 	read-only
 */
export default class RelatedField extends ReadOnlyField{

	/** Constructs the field
	 * 	@param {function} entityClass class for the related entity
	 */
	constructor(entityClass){
		super();
		this.__entityClass = entityClass;
	}

	/** converts the entity field to an object
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from the external source
	 * 	@return {any} 				the value dispatched to the user
	 */
	correct(entity, name, internalValue){
		if (internalValue === null){
			return null;
		}

		let relatedEntity = new this.__entityClass();
		Object.assign(relatedEntity._entityFields, internalValue);
		relatedEntity._state = EntityState.found;
		return relatedEntity;
	}

}