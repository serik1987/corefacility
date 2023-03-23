import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';

import Group from 'corefacility-core/model/entity/Group';
import CoreListEditor from 'corefacility-core/view/base/CoreListEditor';

import GroupList from './GroupList';


/**
 * Provides CRUD operations on the group list
 * 
 * Props:
 * @param {string} searchTerm 		searches groups on name
 * @param 	{callback}	onItemAddOpen		This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 */
export default class GroupListEditor extends CoreListEditor{

	constructor(props){
		super(props);
		this.handleUserRemove = this.handleUserRemove.bind(this);
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let searchTerm = props.searchTerm || '';
		let filter = {q: searchTerm};
		return filter;
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		let searchTerm = props.searchTerm || '';
		return `${searchTerm}`;
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		return t("Group list");
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return t("Add group");
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return GroupList;
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return Group;
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
					onItemSelect={this.handleSelectItem}
					onItemRemove={this.handleItemRemove}
					onUserRemove={this.handleUserRemove}
				/>);
	}

	/**
	 * 	Triggers when the user tries to remove itself from the group
	 * 	@param {SyntheticEvent} event 	the event triggered by the child component
	 */
	async handleUserRemove(event){
		try{
			let group = event.detail;
			this.setState({_isLoading: true, _error: null});
			let answer = await window.application.openModal('question', {
				caption: t("Delete confirmation"),
				prompt: t("Do you really want to exclude yourself from this group?")
			});
			if (!answer){
				return;
			}
			let apiVersion = window.SETTINGS.client_version;
			let userId = window.application.user.id;
			await client.delete(`/api/${apiVersion}/groups/${group.id}/users/${userId}`);
			this.itemListComponent.removeItem(group);
		} catch (error){
			this.setState({_error: error.message});
		} finally{
			this.setState({_isLoading: false});
		}

	}

}