import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';

import GroupUser from './GroupUser';


/**
 * 	Represents all users NOT mentioned in a given group
 */
export default class SuggestedGroupUser extends GroupUser{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Suggested group user";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider("groups/:id:/user-suggest", SuggestedGroupUser),
		];
	}

	/** Creates the entity on the remote service
	 *  @async
	 *  @return {undefined}
	 */
	async create(){
		throw new Error("The suggested user list is read-only");
	}

	/** Deletes the entity from the external source
	 *  @async
	 *  @return {undefined}
	 */
	async delete(){
		throw new Error("The suggested user list is read-only");
	}

}