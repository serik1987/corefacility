import {translate as t} from 'corefacility-base/utils';
import {ValidationError} from 'corefacility-base/exceptions/model';


/** Validators are additional objects that provide field validation
 *  Validators can be attached to the StringField. One StringField
 * 	may accept unlimited number of validators.
 * 
 * 	To attach single validator use the following:
 * 		field
 * 			.addValidator(Validator1)
 * 				.setMessage("Invalid field!'")
 * 				.parent
 * 			.addValidator(Validator2)
 * 				.setSomeProperty(someValue)
 * 				.parent
 * 
 * 	(1) addValidator accepts the validator class (not object!), creates new validator instance
 * 		and attaches this instance to the field. It returns the validator
 * 	(2) You can set any validator properties. Any property setter always return the validator.
 * 	(3) If you want to move from validator instance to the field instance in your method chain
 * 		always use parent property
 */
export default class Validator{

	/** Creates new validator
	 * 	@param {StringField} parent 	field which validator attaches to
	 * 	@param {RegExp} pattern 		The RegExp pattern to be tested. The value is considered
	 * 									to be valid if it matches the pattern. Otherwise, the value
	 * 									is considered to be invalid.
	 * 	@param {string} message 		Message to be printed below the input box when the value is
	 * 									invalid. The printed message will be automatically translated,
	 * 									so, don't use t-function.
	 */
	constructor(parent, pattern, message){
		this._parent = parent;
		this._pattern = pattern;
		this._message = message || "Bad value";
	}

	/** The message will be printed below the input box when the entered value is not valid */
	get message(){
		return t(this._message);
	}

	/** Sets the message that will be printed  at the input box when the entered value is not valid
	 */
	setMessage(message){
		this._message = message;
		return this;
	}

	/** Provides validation itself.
	 * 	@param {string} value 	The value to validate
	 * 	@return {undefined}		The method will return undefined when validation is successful.
	 * 							When validation fails, the validation should throw ValidationError
	 */
	validate(value){
		if (value === null){
			return;
		}
		if (!this._pattern.test(value)){
			throw new ValidationError(this.message);
		}
		return this._pattern.test(value);
	}

	/** StringField this validator has been attached to */
	get parent(){
		return this._parent;
	}

}


/** Validates slugs and aliases (i.e., user's login, project alias etc.) */
export class SlugValidator extends Validator{

	constructor(parent){
		super(parent, /^[-a-zA-Z0-9_]+$/, "This field allows letters, digits, underscores and hyphens");
	}

}


/** Validates E-mails */
export class EmailValidator extends Validator{

	ALLOWED_DOMAIN_LIST = [
		"localhost"
	];


	USER_PART_REGEX = /(^[-!#$%&'*+\/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+\/=?^_`{}|~0-9A-Z]+)*$|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)/i;

	DOMAIN_REGEX = /((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))$/i;

	LITERAL_REGEX = /\[([A-F0-9:.]+)\]$/i;

	constructor(parent){
		super(parent, /^[0-9A-Za-z._\-!#$%&'*+\/=?^_`{}|~]+@[A-Za-z._\-!#$%&'*+\/=?^_`{}|~]+$/, "Incorrect e-mail");
	}

	/** Provides validation itself.
	 * 	@param {string} value 	The value to validate
	 * 	@return {undefined}		The method will return undefined when validation is successful.
	 * 							When validation fails, the validation should throw ValidationError
	 */
	validate(value){
		if (value.search('@') === -1){
			throw new ValidationError(this.message);
		}
		let valueParts = value.split('@');
		let domainPart = valueParts.pop();
		let userPart = valueParts.join('@');
		if (!this.USER_PART_REGEX.test(userPart) || !this.validateDomainPart(domainPart)){
			throw new ValidationError(this.message);
		}
	}

	/** Validates the domain part of the E-mail
	 * 	@param {string} value 	The value to validate
	 * 	@return {undefined}		The method will return undefined when validation is successful.
	 * 							When validation fails, the validation should throw ValidationError
	 */
	validateDomainPart(value){
		if (this.ALLOWED_DOMAIN_LIST.indexOf(value) !== -1){
			return true;
		}

		if (this.DOMAIN_REGEX.test(value) || this.LITERAL_REGEX.test(value)){
			return true;
		}

		return false;
	}

}


/** Validates phone numbers */
export class PhoneValidator extends Validator{

	constructor(parent){
		super(parent, /^\+?[\d\(\)\s\-]+$/, "Incorrect phone number");
	}

}


/** Validates URL */
export class UrlValidator extends Validator{

	constructor(parent){
		super(parent, null, "Invalid URL");
		this._schemes = ["http", "https"];
	}

	/** Sets list of all available schemes
	 * 	@param {Array of String} schemes 		the list of schemes to be used
	 * 	@return {UrlValidator}					instance of the object that invoked the method
	 */
	setSchemes(schemes){
		this._schemes = schemes;
	}

	/** Provides validation itself.
	 * 	@param {string} value 	The value to validate
	 * 	@return {undefined}		The method will return undefined when validation is successful.
	 * 							When validation fails, the validation should throw ValidationError
	 */
	validate(value){
		try{
			let url = new URL(value);
			let scheme = url.protocol.split(":")[0];
			if (this._schemes.indexOf(scheme) === -1){
				throw new ValidationError(this.message);
			}
		} catch (error){
			throw new ValidationError(this.message);
		}
	}

}


/** Validates that the string equals to one of given values */
export class ChoiceValidator extends Validator{

	/** Creates new validator
	 * 	@param {Field} parent 				a field to which the validator belongs to
	 * 	@param {Array of String} choices	list of valid values
	 */
	constructor(parent, choices){
		super(parent, null, "Please, chooice one of the following values: ");
		this.setChoices(choices);
	}

	/** Sets the validator choices
	 * 	@param {Array of String} choices 	list of valid values
	 * 	@return {ChoiceValidator}			instance of the object invoked the method
	 */
	setChoices(choices){
		this._choices = choices;
		return this;
	}

	/** Validation error message
	 */
	get message(){
		let message = super.message;
		if (this._choices instanceof Array){
			message += this._choices.join(", ");
		}
	}

	/** Provides validation itself.
	 * 	@param {string} value 	The value to validate
	 * 	@return {undefined}		The method will return undefined when validation is successful.
	 * 							When validation fails, the validation should throw ValidationError
	 */
	validate(value){
		if (!this._choices){
			throw new ValidationError("ChoiceValidator: call setChoices method to finish the validator attachment");
		}
		if (this._choices.indexOf(value) === -1){
			throw new ValidationError(this.message);
		}
	}

}