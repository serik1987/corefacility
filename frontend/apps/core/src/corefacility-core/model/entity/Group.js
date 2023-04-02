import Entity from 'corefacility-base/model/entity/Entity';
import {StringField, IntegerField} from 'corefacility-base/model/fields';
import RelatedField from 'corefacility-base/model/fields/RelatedField';
import User from 'corefacility-core/model/entity/User';
import GroupProvider from 'corefacility-core/model/providers/GroupProvider';

import GroupUser from './GroupUser';
import SuggestedGroupUser from './SuggestedGroupUser';


/**
 * Represents one single group
 */
export default class Group extends Entity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Scientific Group";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @abstract
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [new GroupProvider(Group)];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @abstract
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			name: new StringField()
				.setDescription("Name")
				.setDefaultValue(null)
				.setRequired(true),
			governor_id: new IntegerField()
				.setDescription("Group leader ID (write-only)")
				.setMinValue(1),
			governor: new RelatedField(User)
				.setDescription("Group leader")
		}
	}

	/**
	 *  Returns all group members, including the superuser
	 * 	@async
	 * 	@return {EntityPage} a page related to all group members
	 */
	getUsers(){
		return this._getChildEntities(GroupUser, {});
	}

	/**
	 *  Returns list of all suggested users
	 * 	@async
	 * 	@return {Array of entity} list of all suggested users
	 */
	getSuggestedUsers(searchParams){
		return this._getChildEntities(SuggestedGroupUser, searchParams);
	}

}