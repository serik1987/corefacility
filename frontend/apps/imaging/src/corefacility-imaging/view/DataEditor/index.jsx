import SidebarEditor from 'corefacility-base/view/SidebarEditor';
import FunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import DataList from '../DataList';
import style from './style.module.css';


/**
 * 	Represents list of functional maps together with facilities for uploading and downloading a single map.
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param 	{Number} 	lookup 					ID of the map to open on the right side. undefined will not open any map
 * 												on the right side
 * 	@param 	{callback}	onItemAddOpen			This is an asynchronous method that opens
 * 												add entity box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 *  @param {callback} onItemChangeOpen          An asynchronous method that opens each time the user opens the modify
 *                                              entity box (either page or modal box). The promise always fulfills when
 *                                              the user close the box. The promise can be never rejected.
 * 
 *	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  You can manage loading state through reportListFetch(), reportFetchSuccess(itemList), reportFetchFailure(error)
 *  @param {Number} itemId                      ID of the item to open.
 *  @param {Entity} item                        The item currently selected by the user.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 *  @param {Number}   itemId                    ID of the opened item.
 *  @param {callback} onItemOpen                This method must be triggered when the user tries to open the item on
 *                                              the right pane.
 * 	@param {callback} onItemSelect				This method must be triggered when the user tries to change the item.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class DataEditor extends SidebarEditor{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return FunctionalMap;
	}

	/**
     *  Returns item lookup that shall be inserted to the Entity.get method
     *  @param {Number}     id          ID of the item
     *  @return {Array}                 Array if IDs that include ID of the item, ID of parent iten etc,,,,
     *                                  (see Entity,get() for details)
     */
    getLookup(id){
        return {
        	parent: window.application.project,
        	id: id,
        }
    }

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return DataList;
	}

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the request)
	 */
	async _fetchList(filter){
		return await window.application.project.getMaps(filter);
	}

	/** Uses the component props (and probably state?) to identify the filter.
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
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		return '';
	}

	/**
     *  Renders the right pane of the sidebar.
     */
    renderRightPane(){
    	console.log(this.state.item && this.state.item.toString());
        return (
        	<div className={style.main}>
        		<div className={style.uploader_row}>
        			<div className={style.uploader}>Rendering the uploader...</div>
        			<div className={style.mat_downloader}>MAT</div>
        			<div className={style.npy_downloader}>NPY</div>
        		</div>
        		<div className={style.map_viewer}>Rendering the map viewer...</div>
        	</div>	
        );
    }
}