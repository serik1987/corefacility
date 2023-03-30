import {translate as t} from 'corefacility-base/utils';
import {NotFoundError} from 'corefacility-base/exceptions/network';
import EntityPage from 'corefacility-base/model/EntityPage';

import Project from 'corefacility-core/model/entity/Project';
import CoreListEditor from 'corefacility-core/view/base/CoreListEditor';

import ProjectApplicationList from './ProjectApplicationList';


/** 
 * 	Allows the user to manage application list.
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 		@param {string} projectLookup 			Alias of the project to lookup
 * 		@param {callback} on404 				Will be triggered when no project has been found
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching(), reportListSuccess(items) and
 * 		reportListFailure(error) instead of them.
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
export default class ProjectApplicationListEditor extends CoreListEditor{

	constructor(props){
		super(props);

		this._project = null;
	}

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the )
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
				} else {
					throw error;
				}
				return EntityPage.empty();
			}
		}

		let searchParams = this.deriveFilterFromPropsAndState(this.props, this.state);
		return await this._project.getApplicationList(searchParams);
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return ProjectApplicationList;
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return null;
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		return {}
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
		return '';
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		return (this._project && this._project.name) || t("Project application list");
	}

	/** Renders the item list.
	 *  This function must be invoked from the render() function.
	 */
	renderItemList(){
		let ItemList = this.entityListComponent;
		return (<ItemList
					project={this._project}
					items={this.itemList}
					isLoading={this.isLoading}
					isError={this.isError}
					ref={this.registerItemList}
					onItemAdd={this.handleItemAdd}
					onItemSelect={this.handleSelectItem}
					onItemRemove={this.handleItemRemove}
				/>);
	}

}