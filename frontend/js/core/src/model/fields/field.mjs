import {ValidationError} from '../../exceptions/model.mjs';
import {translate as t} from '../../utils.mjs';


/** Entity field is a special object that provides an additional
 *  validation control for the value entered to the entity.
 * 
 *  The entity fields are usually added to the entity and instantiated
 *  when the entity creates
 */ 
export default class EntityField{

	pattern = null;

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
	constructor(defaultValue, valueType, description, required, pattern){
		this._defaultValue = defaultValue;
		this._valueType = valueType;
		this._description = description;
		this._required = required;
		this._validators = [];
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

	/** Adds new string validator
	 * 		@param {object} validator 	a simple object with the following fields:
	 * 			@oaram {RegExp} pattern 	a RegExp pattern. The field is considered to be valid
	 * 										if its valid matches this pattern.
	 * 			@param {function} message 	A message to show if the field is invalid.
	 * 										A message is represented in form of some function that accepts
	 * 										no arguments and returns error message to show
	 * 		@return {EntityField}	this entity. So, you can use similar methods in chain.
	 */
	addValidator(validator){
		this._validators.push(validator);
		return this;
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
		if (value === null && this.required){
			throw new ValidationError(t("Required field."));
		}
		if (typeof value !== this._valueType && value !== null){
			throw new TypeError("Bad type of the property value");
		}
		if (value !== null){
			this.validate(value);
		}
		return value;
	}

	/** Validates the value
	 * 		@param {any} the valye to be validated
	 * 		@return {undefined
	 */
	validate(value){
		for (let validator of this._validators){
			if (!validator.pattern.test(value)){
				throw new ValidationError(validator.message());
			}
		}
	}

}

EntityField.slugValidator = {

	pattern: /^[-a-zA-Z0-9_]+$/,

	message: function(){
		return t(`Enter a valid {field_name} consisting of letters, numbers, underscores or hyphens.`)
			.replace("{field_name}", this.name);
	},

	setFieldName: function(name) {
		this.name = name.toLowerCase();
		return this;
	}
};

EntityField.emailValidator = {

	pattern: /^[0-9A-Za-z._\-!#$%&'*+\/=?^_`{}|~]+@[A-Za-z._\-!#$%&'*+\/=?^_`{}|~]+$/,

	message: () => t("Incorrect e-mail"),
}

EntityField.phoneValidator = {

	pattern: /^\+?[\d\(\)\s\-]+$/,

	message: () => t("Incorrect phone number")
}