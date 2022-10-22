/** Entity field is a special object that provides an additional
 *  validation control for the value entered to the entity.
 * 
 *  The entity fields are usually added to the entity and instantiated
 *  when the entity creates
 */ 
export default class EntityField{

	/** Creates the entity field
	 *  @param {any} defaultValue value that will be assigned to the entity field
	 *               if nothing was specified. Such a value will not be sent to the
	 * 				 entity provider
	 *  @param {string} valueType value type check: if typeof field_value is not the
	 *                            same as this argument, TypeError will be thrown
	 *  @param {string} description A human-readable entity description that will be
	 *                              applied when you transform entity to string using
	 *                              toString() function
	 *  @param {boolean} required True if the entity field is required, false otherwise
	 */
	constructor(defaultValue, valueType, description, required){
		this._defaultValue = defaultValue;
		this._valueType = valueType;
		this._description = description;
		this._required = required;
	}

	/** Default value */
	get default(){
		return this._defaultValue;
	}

	/** Field description */
	get description(){
		return this._description;
	}

	/* true if the field is required, false otherwise */
	get required(){
		return this._required;
	}

	/** Moves the field value from the internal entity state to the entity user
	 *  @param {any} internalValue value in the entity state
	 *  @param {any} the field value represented to the entity user
	 */
	correct(internalValue){
		return internalValue;
	}

	/** Moves the field value from the entity user to the internal entity state
	 *  @param {string} entityName name of the entity which value is intended to be saved
	 *  @param {string} propertyName  field name
	 *  @param {any} value the field value given by the entity user
	 *  @return {any} the value to be stored in the entity
	 */
	proofread(entityName, propertyName, value){
		if (typeof value !== this._valueType){
			throw new TypeError("Bad type of the property value");
		}
		return value;
	}

}