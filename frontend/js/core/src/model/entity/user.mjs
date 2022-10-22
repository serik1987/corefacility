import Entity from './base.mjs';
import EntityField from '../fields/field.mjs';
import ReadOnlyField from '../fields/read-only-field.mjs';
import HttpRequestProvider from '../providers/http-request.mjs';



/** The User entity contains information about the user that allows to set up
 *  the authorization and permission properties and stores user's personal data
 *  (e-mail and phone number)
 * 
 *  Fields:
 * 		@param {int} id 				 unique user identifier
 * 		@param {string} login			 small alias that will be used for the standard authorization
 * 		@param {boolean} is_password_set true if the password has been set and delivered to the user
 *                                       false if not. In this case the user can't be authorized
 * 		@param {string} name			 The user's first name (to be used for visualization)
 * 		@param {string} surname			 The user's last name (to be used for visualization)
 * 		@param {string} e-mail			 The user's e-mail (to be used for the password recovery system)
 * 		@param {string} phone			 The user's phone number (to be called in case of suspicious operations)
 * 		@param {boolean} is_locked		 true if the user cant' login using any authorization method, false otherwise
 * 		@param {boolean} is_superuser	 true if the user has superuser priviledges, false otherwise
 * 		@param {boolean} is_support	     true if the user is 'support' user (used for automatic login), false otherwise
 * 		@param {string} unix_group		 name of the POSIX account corresponding to the user
 * 		@param {string} home_dir		 directory where user personal files were located
 * 
 * Entity providers:
 * 		HttpRequestProvider - information exchange with the Web Server
 */
export default class User extends Entity{

	static get _entityName(){
		return "User";
	}

	static _definePropertyDescription(){
		return {
			"login": new EntityField(null, 'string', "Login", true),
			"avatar": new ReadOnlyField("Avatar URL"),
			"is_password_set": new ReadOnlyField("Is user password was set"),
			"name": new EntityField(undefined, 'string', "First Name", false),
			"surname": new EntityField(undefined, 'string', "Surname", false),
			"email": new EntityField(undefined, 'string', "E-mail", false),
			"phone": new EntityField(undefined, "string", "Phone number", false),
			"is_locked": new EntityField(false, "boolean", "Is user locked", false),
			"is_superuser": new EntityField(false, "boolean", "Has administrator rights", false),
			"is_support": new ReadOnlyField("Is support user"),
			"unix_group": new ReadOnlyField("POSIX user"),
			"home_dir": new ReadOnlyField("POSIX home directory"),
		}
	}

	static _defineEntityProviders(){
		return [new HttpRequestProvider('users', User)];
	}

	toString(){
	    return super.toString();
	}

}