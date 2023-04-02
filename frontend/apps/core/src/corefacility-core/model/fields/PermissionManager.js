import {NotImplementedError} from 'corefacility-base/exceptions/model';
import EntityState from 'corefacility-base/model/entity/EntityState';
import client from 'corefacility-base/model/HttpClient';

import Group from 'corefacility-core/model/entity/Group';
import AccessLevel from 'corefacility-core/model/entity/AccessLevel';


/**
 *  This is the base class that allows to manage entity permissions
 */
export default class PermissionManager{

	/**
	 *  Creates permission manager
	 * 	@param {Entity} entity 		entity which permissions must be considered.
	 */
	constructor(entity){
		this._entity = entity;
	}

	/**
	 *  Returns 'prj' for ProjectPermissionManager and 'app' for application permission manager
	 */
	static getLevelType(){
		throw new NotImplementedError('getLevelType');
	}

	/**
	 * 	Returns list of all access levels
	 * 	@async
	 * 	@return access level list
	 */
	static async getAccessList(){
		if (this.__accessList === undefined){
			this.__accessList = [... await AccessLevel.find({type: this.getLevelType()})];

		}
		for (let accessLevel of this.__accessList){
			if (accessLevel.alias === 'full'){
				this.__fullAccessLevel = accessLevel;
			} else if (accessLevel.alias === 'no_access'){
				this.__noAccessLevel = accessLevel;
			}
		}

		return this.__accessList;
	}

	/**
	 *  Returns the full access level
	 */
	static get fullLevel(){
		if (!this.__fullAccessLevel){
			throw new Error("Please, call getAccessList method in advance and wait promise to be fulfilled");
		}
		return this.__fullAccessLevel;
	}

	static get noAccessLevel(){
		if (!this.__noAccessLevel){
			throw new Error("Please, call getAccessList method in advance and wait promise to be fulfilled");
		}
		return this.__noAccessLevel;
	}


	/**
	 *  URL for the permission list seeking/updating
	 */
	get permissionListUrl(){
		throw new NotImplementedError("get permissionListUrl");
	}

	processResultItem(resultItem){
		let group = Group.searchEntityProvider.getObjectFromResult({
			id: resultItem.group_id,
			name: resultItem.group_name
		});
		let accessLevel = AccessLevel.searchEntityProvider.getObjectFromResult({
			id: resultItem.access_level_id,
			type: this.constructor.getLevelType(),
			alias: resultItem.access_level_alias,
			name: resultItem.access_level_name,
		});
		return {group: group, level: accessLevel};
	}

	/**
	 * 	Retrieves list of all entity permissions
	 * 	@async
	 * 	@return an object with the following properties:
	 * 		@param {Group} group 				a group which permissions are ascribed
	 * 		@param {AccessLevel} accessLevel	an access level to adjust
	 */
	async find(){
		await this.constructor.getAccessList();
		let queryResult = await client.get(this.permissionListUrl);
		let methodResult = queryResult.map(this.processResultItem.bind(this));
		return methodResult;
	}

	/**
	 * 	Modifies the permission
	 * 	@async
	 * 	@param {Number} groupId 		ID of the group which permission must be modified
	 * 	@param {Number} levelId 		ID of the new access level for this group
	 * 	@return an object with the following properties:
	 * 		
	 */
	async set(groupId, levelId){
		let result = await client.post(this.permissionListUrl, {
			group_id: groupId,
			access_level_id: levelId,
		});
		return this.processResultItem(result);
	}

	/**
	 *  Removes permission from the list
	 * 	@async
	 * 	@param {Number} groupId 		ID of the group which permission will be removed
	 */
	async remove(groupId){
		let url = `${this.permissionListUrl}${groupId}/`
		await client.delete(url);
	}

}
