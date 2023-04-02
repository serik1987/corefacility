import FieldManager, {ManagedField} from 'corefacility-base/model/fields/FieldManager';
import client from 'corefacility-base/model/HttpClient';


/**
 * Fields that allows the user to set its own password
 */
export default class PasswordField extends ManagedField{

	constructor(){
		super(PasswordManager);
	}

	get default(){
		return this.correct(null, null, null);
	}

}


/**
 * Allows the user to set its own password
 */
export class PasswordManager extends FieldManager{

	/** Creates new FieldManager
	 * 	@param {Entity} entity 			Useless
	 * 	@param {string} propertyName 	Useless
	 * 	@param {any} defaultValue		Useless
	 * 	@param {object} options 		Useless
	 */
	constructor(entity, propertyName, defaultValue, options){
		super(entity, propertyName, defaultValue);
		this.__value = null;
	}

	get value(){
		return this.__value;
	}

	/**
	 * Requests the Web server to generate the user's password
	 * @async
	 * @return {string} the user's password itself
	 */
	async generate(){
		let apiVersion = window.SETTINGS.client_version;
		let result = await client.post(`/api/${apiVersion}/profile/password-reset/`);
		this.__value = result.password;
		return this.__value;
	}

	toString(){
		if (this.value === null){
			return '***';
		} else {
			return this.value;
		}
	}

}