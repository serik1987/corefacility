import {ReadOnlyPropertyError} from '../../exceptions/model.mjs';
import EntityField from './fields.mjs';


/** Sometimes the server doesn't allow to modify the field directly
 *  using the PUT/PATCH request but provides plenty of methods that
 * 	allow to do it indirectly by plenty of another API functions.
 * 
 * 	Example of such fields are avatar, password and so on.
 * 
 * 	The FieldManager allows the following access to fields
 * 	await someEntity.someField.someMethod(...)
 * 		You can call various manager methods to change
 * 		field values indirectly
 * 
 * 	When you use field manager, the field access is the following:
 * 	someEntity.someField 	Returns instance of field manager itself
 * 	someEntity.someField = someValue 	ERROR! Don't do it!
 * 
 * 	The field manager is created during the first access to the field
 * 	(first after entity instantiation!). Each following access to the
 * 	field revoke the previously created field manager.
 */
export default class FieldManager{

	/** Creates new FieldManager
	 * 	@param {Entity} entity 			Entity the field belongs to
	 * 	@param {string} propertyName 	Modifying property name
	 * 	@param {any} defaultValue		Default field value.
	 * 	@param {object} options 		Implementation-dependent options
	 */
	constructor(entity, propertyName, defaultValue, options){
		this._entity = entity;
		this._propertyName = propertyName;
		this._internalValue = defaultValue;
	}

	/** The entity to which the field is attached */
	get entity(){
        return this._entity;
    }

    /** The field name inside the entity to which the field is attached */
    get propertyName(){
    	return this._propertyName;
    }

	/** The internal value*/
	get internalValue(){
		return this._internalValue;
	}

	set internalValue(value){
		this._internalValue = value;
	}

}


/** Represents an entity field which access is provided solely
 * 	throw the field manager.
 * 
 * WARNING! THE FIELD OBJECT is UNIFIED for all entities belonging to
 * a given class. It should NOT contain information related to a given
 * entity (i.e., field values, field managers etc.)
 */
export class ManagedField extends EntityField{

	/** Constructs the managed entity field
	 * 	@param {function} managerClass 		an instance of this class will be
	 * 										created upon request.
	 *	@param {object} options				options to be passed to the entity manager.
	 */
	constructor(managerClass, options){
		super();
		this._managerClass = managerClass;
		this._options = options || {};
	}


	/** Provides read-only access to the managed field
	 * 	@param {Entity} entity 	entity which field must be accessed
	 * 	@param {string} propertyName 	The field to be accessed
	 * 	@param {any} internalValue 		The value returned by entity's GET request
	 * 	@return {FieldManager} the manager to instantiate
	 */
	correct(entity, propertyName, internalValue){
		this._manager = new this._managerClass(entity, propertyName,
				this.defaultValue, this._options);
		this._manager.internalValue = internalValue;
		return this._manager;
	}

	/** Always throw an exception to indicate that setting this field is not allowed */
	proofread(entity, propertyName, value){
		throw new ReadOnlyPropertyError(entity.constructor._entityName, propertyName);
	}

}
