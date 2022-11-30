import {translate as t} from 'corefacility-base/utils';

import Entity from 'corefacility-base/model/entity/Entity';
import {StringField, BooleanField, ReadOnlyField} from 'corefacility-base/model/fields';
import FileField from 'corefacility-base/model/fields/FileField';
import {SlugValidator, EmailValidator, PhoneValidator} from 'corefacility-base/model/validators';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';



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

			"login": new StringField()
				.setDefaultValue(null)
				.setRequired()
				.setDescription("Login")
				.addValidator(SlugValidator)
					.setMessage("Enter a valid user name consisting of letters, numbers, underscores or hyphens.")
					.parent,

			"avatar": new FileField(entity => `users/${entity.id}/avatar/`)
				.setDescription("User's avatar"),

			"is_password_set": new ReadOnlyField()
				.setDescription("Is user password was set"),

			"name": new StringField()
				.setDescription("Name"),

			"surname": new StringField()
				.setDescription("Surname"),

			"email": new StringField()
				.setDescription("E-mail")
				.addValidator(EmailValidator)
					.parent,

			"phone": new StringField()
				.setDescription("Phone number")
				.addValidator(PhoneValidator)
					.parent,

			"is_locked": new BooleanField()
				.setDescription("Is user locked"),

			"is_superuser": new BooleanField()
				.setDescription("Has administrator rights"),

			"is_support": new ReadOnlyField()
				.setDescription("Is support user"),

			"unix_group": new ReadOnlyField()
				.setDescription("POSIX user"),

			"home_dir": new ReadOnlyField()
				.setDescription("POSIX home directory"),
		}
	}

	static _defineEntityProviders(){
		return [new HttpRequestProvider('users', User)];
	}

	toString(){
	    return super.toString();
	}

}