import EntityPage from 'corefacility-base/model/EntityPage';
import Group from 'corefacility-base/model/entity/Group';

import CoreListEditor from 'corefacility-core/view/base/CoreListEditor';

import GroupUserList from './GroupUserList';


/** 
 *  Deals with all users containing in a certain group
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 		@param 	{callback}	onItemAddOpen		This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 		@param {int} groupId				 	The group which user list shall be displayed
 * 		@param {Group} group 					A group to be loaded
 * 		@param {string} name 					The header name
 * 		@param {callback} on404					Triggers when a particular group has not been found
 * 		@param {callback} onGroupFound			Triggers when the group has been found. Arguments:
 * 												@param {Group} group a group that was found
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 * 		@param {callback} onItemSelect			This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 		@param {callback} onItemRemove 			This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 * 		@param {Group} group 					The group to be uploaded
 */
export default class GroupListEditor extends CoreListEditor{

	constructor(props){
		super(props);

		this._group = null;
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		return this.props.name;
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return null;
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return GroupUserList;
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

	/**
     * Downloads the entity list from the Web server
     * @param {oject} filter        Filter options to be applied
     *                              (These options will be inserted to the )
     */
    async _fetchList(filter){
    	if (this.props.group){
    		this._group = this.props.group;
    	}

    	if (this._group === null){
    		this._group = await this.getEntityOr404(() => Group.get(this.props.groupId));
    		if (this.props.onGroupFound){
    			this.props.onGroupFound(this._group);
    		}
    	}

    	return await this._group.getUsers();
    }

}
