import ChildEntity from 'corefacility-base/model/entity/ChildEntity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {ReadOnlyField, IntegerField} from 'corefacility-base/model/fields';


/**
 * 	Represents information about the user's presence inside the group
 */
export default class GroupUser extends ChildEntity{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Group User";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider("groups/:id:/users", GroupUser),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			'login': new ReadOnlyField().setDescription("login"),
			'name': new ReadOnlyField().setDescription("First Name"),
			'surname': new ReadOnlyField().setDescription("Last Name"),
			'avatar': new ReadOnlyField().setDescription("Avatar URL"),
			'user_id': new IntegerField()
				.setDescription('User ID (write-only)')
				.setMinValue(1),
		};
	}

	/** This is a static method that downloads entity with a given ID or alias
	 *  @async
	 *  @static
	 *  @param {int|string} lookup the entity ID or alias
	 *  @return {Entity} the entity to be returned
	 */
	static async get(lookup){
		throw new Error("The feature has not been present in the parent entity");
	}

	/** Saves all entity changes to the hard disk.
	 *  @async
	 *  @return {undefined}
	 */
	async update(){
		throw new Error("The GroupUser is read-only entity. Use User entity instead.");
	}

}