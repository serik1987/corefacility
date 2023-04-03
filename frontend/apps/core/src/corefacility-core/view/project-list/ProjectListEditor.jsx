import {translate as t} from 'corefacility-base/utils';
import Project from 'corefacility-base/model/entity/Project';

import CoreListEditor from 'corefacility-core/view/base/CoreListEditor';

import ProjectList from './ProjectList';


/** This is a base class for user, project and group list editors
 *  styled in the following way:
 * 		- Add entity button is at the top-right corner;
 * 		- The list editor starts from header;
 *      - error / loading / information message is at the top of the editor;
 *      - list of entities satisfying given conditions is below
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
 * 
 * 		@p
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
 */
export default class ProjectListEditor extends CoreListEditor{

	/** Uses the component props (and probably state?) to identify the filter.
	 *  @abstract
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let searchParams = {};
		if (props.searchTerm){
			searchParams.q = props.searchTerm;
		}
		return searchParams;
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
		return props.searchTerm ? props.searchTerm : '';
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		return t("Project List");
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return t("Create New Project");
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return Project;
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return ProjectList;
	}

}