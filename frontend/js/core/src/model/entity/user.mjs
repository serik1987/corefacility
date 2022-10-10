import Entity from './base.mjs';
import EntityField from '../fields/field.mjs';
import HttpRequestProvider from '../providers/http-request.mjs';

export default class User extends Entity{

	static get _entityName(){
		return "User";
	}

	static _definePropertyDescription(){
		return {
			"login": new EntityField(null, 'string', "Login"),
			"name": new EntityField(undefined, 'string', "First Name"),
			"surname": new EntityField(undefined, 'string', "Surname"),
			"email": new EntityField(undefined, 'string', "email"),
		}
	}

	static _defineEntityProviders(){
		return [new HttpRequestProvider('users', User)];
	}

	toString(){
	    return super.toString();
	}

}