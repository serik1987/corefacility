import {translate as t} from 'corefacility-base/utils';
import {NotFoundError} from 'corefacility-base/exceptions/network';

import Project from 'corefacility-core/model/entity/Project';
import ProjectPermissionManager from 'corefacility-core/model/fields/ProjectPermissionManager';
import CoreListEditor from 'corefacility-core/view/base/CoreListEditor';
import PermissionList from 'corefacility-core/view/base/PermissionList';


/** Allows the user to change project permissions
 * 
 *  Props:
 * 		@param {string} projectLookup 			Lookup of the project which permissions must be adjusted
 * 		@param {callback} on404 				Will be triggered when no such project exists
 * 
 *	State:
 * 		Loading/error states are accessible through reportListFetching, reportFetchSuccess and reportFetchFailure
 * 		methods
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 *      @param {callback} onItemAdd             This method must be triggered the the user adds an entity to
 *                                              the entity list by means of the entity list facility
 * 		@param {callback} onItemSelect			This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 		@param {callback} onItemRemove 			This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class ProjectPermissionEditor extends CoreListEditor{

	constructor(props){
		super(props);
		this.handlePermissionAdd = this.handlePermissionAdd.bind(this);
		this.handlePermissionSet = this.handlePermissionSet.bind(this);
		this.handlePermissionRemove = this.handlePermissionRemove.bind(this);

		this._project = null;
		this._accessLevelList = [];
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return PermissionList;
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 *  @abstract
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		return {};
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@abstract
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		return '';
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		if (this._project === null){
			return t("Project administration");
		} else {
			return this._project.name;
		}
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return null;
	}

	/**
	 * 	Downloads the entity list from the Web server
	 * 	@async
	 * 	@param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the query)
	 */
	async _fetchList(filter){
		if (this._project === null){
			try{
				this._project = await Project.get(this.props.projectLookup);
			} catch (error){
				if (error instanceof NotFoundError){
					if (this.props.on404){
						this.props.on404();
					}
					return [];
				} else {
					throw error;
				}
			}
		}

		let permissions = this._project.permissions;
		this._accessLevelList = (await ProjectPermissionManager.getAccessList())
			.map(accessLevel => {return {value: accessLevel.id, text: accessLevel.name}});
		return await permissions.find();
	}

	/** Renders the item list.
	 *  This function must be invoked from the render() function.
	 */
	renderItemList(){
		let ItemList = this.entityListComponent;
		return (<ItemList
					items={this.itemList}
					isLoading={this.isLoading}
					isError={this.isError}
					ref={this.registerItemList}
					accessLevelList={this._accessLevelList}
					onPermissionAdd={this.handlePermissionAdd}
					onPermissionSet={this.handlePermissionSet}
					onPermissionRemove={this.handlePermissionRemove}
				/>);
	}

	/**
	 * 	Triggers when the user tries to add the permission
	 * 	@async
	 * 	@param {int} groupId 	ID of the group to add
	 */
	async handlePermissionAdd(groupId){
		try{
			this.reportListFetching();
			let newPermissionItem =
				await this._project.permissions.set(groupId, ProjectPermissionManager.noAccessLevel.id);
			this.itemListComponent.addItem(newPermissionItem);
		} catch (error){
			this.reportFetchFailure(error);
		} finally{
			this.setState({_isLoading: false});
		}
	}

	/**
	 * 	Triggers when the user tries to change the permission
	 * 	@async
	 * 	@param {int} groupId	ID of the group which permissions must be changed
	 * 	@param {int} levelId	ID of the new permission level
	 */
	async handlePermissionSet(groupId, levelId){
		try{
			this.reportListFetching();
			let newPermissionItem = await this._project.permissions.set(groupId, levelId);
			this.itemListComponent.modifyItem(newPermissionItem);
		} catch (error){
			this.reportFetchFailure(error);
			throw error;
		} finally {
			this.setState({_isLoading: false});
		}
	}

	/**
	 *  Triggers when the user tries to remove permission for a given group
	 * 	@async
	 * 	@param {int} groupId 	ID of a group which permission must be removed
	 */
	async handlePermissionRemove(groupId){
		try{
			this.reportListFetching();
			await this._project.permissions.remove(groupId);
			this.itemListComponent.removeItem(groupId);
		} catch (error){
			this.reportFetchFailure(error);
		} finally {
			this.setState({_isLoading: false});
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.onNoRootGroup && this._project &&
				!window.application.user.is_superuser &&
				this._project.governor.id !== window.application.user.id){
			this.props.onNoRootGroup();
		}
	}

}