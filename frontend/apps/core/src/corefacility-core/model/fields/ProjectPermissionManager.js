import PermissionManager from './PermissionManager';


/**
 * 	Managers project permission list
 */
export default class ProjectPermissionManager extends PermissionManager{

	/**
	 *  Returns 'prj' for ProjectPermissionManager and 'app' for application permission manager
	 */
	static getLevelType(){
		return 'prj';
	}

	/**
	 *  URL for the permission list seeking/updating
	 */
	get permissionListUrl(){
		return `/api/${window.SETTINGS.client_version}/projects/${this._entity.id}/permissions/`;
	}

	/**
	 * 	Retrieves list of all entity permissions
	 * 	@async
	 * 	@generator
	 * 	@return an object with the following properties:
	 * 		@param {Group} group 				a group which permissions are ascribed
	 * 		@param {AccessLevel} accessLevel	an access level to adjust
	 */
	async find(){
		let methodResult = await super.find();
		let rootGroup = this._entity.root_group;
		rootGroup.tag = {readOnlyPermission: true};
		methodResult.unshift({
			group: rootGroup,
			level: this.constructor.fullLevel,
		});
		return methodResult;
	}

}