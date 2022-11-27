import Validator from './validators.mjs';
import {translate as t} from '../../utils.mjs';
import {ValidationError, ReadOnlyPropertyError} from '../../exceptions/model.mjs';


/** Entity field is a special object that provides an additional
 *  validation control for the value entered to the entity.
 * 
 *  The entity fields are usually added to the entity and instantiated
 *  when the entity creates
 */ 
export default class EntityField{

	/** Creates the entity field
	 *  @param {string} valueType value type check: if typeof field_value is not the
	 *                            same as this argument, TypeError will be thrown
	 */
	constructor(valueType){
		this._defaultValue = undefined;
		this._valueType = valueType;
		this._required = false;
	}

	/** Default value */
	get default(){
		return this._defaultValue;
	}

	/** Sets the default value.
	 * 	Default value is a value of the property when the form is in CREATING state or 
	 * 	value was not returned by the GET request
	 * 	@param {string} the default 
	 * 	@return {EntityField} this
	 */
	setDefaultValue(defaultValue){
		this._defaultValue = defaultValue;
		return this;
	}

	/** Field description */
	get description(){
		return this._description;
	}

	/** Sets the field description. The field description is used only during the entity print
	 * 	@param {string} description The description to be printed
	 * 	@return {EntityField} this
	 */
	setDescription(description){
		this._description = description;
		return this;
	}

	/* true if the field is required, false otherwise */
	get required(){
		return this._required;
	}

	/** Marks the field as 'required'
	 * 	@param {boolean} value of the field (default true)
	 * 	@return {EntityField} this
	 */
	setRequired(value = true){
		this._required = value;
		return this;
	}

	/** accepts value received from the external source and returns value that will be transmitted to
	 * 		React.js components
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from the external source
	 * 	@return {any} 				the value dispatched to the user
	 */
	correct(entity, name, internalValue){
		return internalValue;
	}

	/** Accepts value from the React.js component and returns the value that will be sent to the
	 * 		external source.
	 * 	Also this method provides validation and must throw ValidationError if the value provided
	 * 		by the React.js components are not valid
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from React.js components
	 * 	@return {any} 				Value that will be sent to external source
	 */
	proofread(entity, propertyName, value){
		if (value === null && this.required){
			throw new ValidationError(t("Required field."));
		}
		if (typeof value !== this._valueType && value !== null){
			throw new TypeError("Bad type of the property value");
		}
		return value;
	}
}


/** Field that accepts string value. Empty string value is the same to null
 */
export class StringField extends EntityField{

	constructor(){
		super('string');
		this._validators = [];
	}

	/** Accepts value from the React.js component and returns the value that will be sent to the
	 * 		external source.
	 * 	Also this method provides validation and must throw ValidationError if the value provided
	 * 		by the React.js components are not valid
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from React.js components
	 * 	@return {any} 				Value that will be sent to external source
	 */
	proofread(entity, propertyName, value){
		if (value === ""){
			value = null;
		}
		let internalValue = super.proofread(entity, propertyName, value);
		if (value !== null){
			this.validate(internalValue);
		}
		return internalValue;
	}

	/** Adds new string validator
	 * @param {function} ValidatorClass 	Class that will be used to construct a given validator.
	 * @return {Validator} newly created validator
	 */
	addValidator(ValidatorClass){
		let validator = new ValidatorClass(this);
		if (!(validator instanceof Validator)){
			throw new Error("The ValidatorClass must be a subclass of the Validator");
		}
		this._validators.push(validator);
		return validator;
	}

	/** Validates the value
	 * 		@param {any} the valye to be validated
	 * 		@return {undefined
	 */
	validate(value){
		for (let validator of this._validators){
			validator.validate(value);
		}
	}
}

/** Fields that accept only two values: true or false */
export class BooleanField extends EntityField{
	constructor(){
		super('boolean');
	}
}


/** Fields that accepts any numbers */
export class NumberField extends EntityField{

	constructor(){
		super('number');
	}
	
}

/** Field that accepts integer numbers only */
export class IntegerField extends EntityField{

	mask = /^[+\-]?\d+$/;

	constructor(){
		super('number');
		this._minValue = -Infinity;
		this._maxValue = Infinity;
	}

	setMinValue(value){
		this._minValue = value;
		return this;
	}

	/** Sets the maximum value of the widget.
	 * 
	 * 	Nobody can't be greater than this maximum value.111
	 */
	setMaxValue(value){
		this._maxValue = value;
		return this;
	}

	/** Accepts value from the React.js component and returns the value that will be sent to the
	 * 		external source.
	 * 	Also this method provides validation and must throw ValidationError if the value provided
	 * 		by the React.js components are not valid
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from React.js components
	 * 	@return {any} 				Value that will be sent to external source
	 */
	proofread(entity, propertyName, value){
		if (value === null || !value.match(this.mask)){
			throw new ValidationError(t("The value must be an integer value"));
		}
		let internalValue = parseInt(value);
		if (internalValue < this._minValue){
			throw new ValidationError(t("The entered value can't be less than ") + this._minValue);
		}
		if (internalValue > this._maxValue){
			throw new ValidationError(t("The entered value can't be greater than ") + this._maxValue);
		}
		return internalValue;
	}

}


/** Field that can be read-only */
export class ReadOnlyField extends EntityField{

	constructor(){
		super(undefined);
	}

	/** Always throw an exception to indicate that setting this field is not allowed */
	proofread(entity, propertyName, value){
		throw new ReadOnlyPropertyError(entity.constructor._entityName, propertyName);
	}

}


/** Read-only field that contains dates only */
export class ReadOnlyDateField extends ReadOnlyField{

	/** Converts the data from ISO format to Javascript's Date object
	 *  @param {Entity} entity 		The Entity this value belongs to
	 * 	@param {string} name 		Name of the entity field
	 * 	@param {any} value 			Value received from the external source
	 * 	@return {any} 				the value dispatched to the user
	 */
	correct(entity, name, internalValue){
		return new Date(internalValue);
	}

}
