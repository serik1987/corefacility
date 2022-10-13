import Entity from './base.mjs';
import EntityField from '../fields/field.mjs';
import ReadOnlyField from '../fields/read-only-field.mjs';
import HttpRequestProvider from '../providers/http-request.mjs';

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