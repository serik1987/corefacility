import client from 'corefacility-base/model/HttpClient';

import FunctionalMapDrawingEditor from './FunctionalMapDrawingEditor';
import PinwheelGraphicList from './PinwheelGraphicList';
import PinwheelList from './PinwheelList';


/**
 * 	Provides CRUD operations on pinwheels.
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback}	onItemAddOpen			This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 
 * 	@param {Number} 	reloadTime 				Timestamp of the last reload. Must be equal to 'reloadDate' state of
 * 												the parent 'Application' component
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
 * 	@param {callback} onItemAddOpen 			This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 */
export default class PinwheelEditor extends FunctionalMapDrawingEditor{

	/**
     *  Returns the graphic item list
     */
    get graphicItemListComponent(){
        return PinwheelGraphicList;
    }

    /** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return PinwheelList;
	}

	/**
     *  Defines props for the child GraphicList component
     */
    get graphicItemListComponentProps(){
    	return {
    		...super.graphicItemListComponentProps,
    		onPinwheelDistance: () => this.handlePinwheelDistance(),
    	}
    }

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the )
	 */
	async _fetchList(filter){
		if (window.application.functionalMap){
			return await window.application.functionalMap.getPinwheelList(filter);
		} else {
			return [];
		}
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
	 * 	Calculates the distance to the nearest pinwheel center
	 * 	@async
	 */
	async handlePinwheelDistance(){
		try{
			this.reportListFetching();
			let url = `/api/${window.SETTINGS.client_version}/core/` +
				`projects/${window.application.project.id}/imaging/` +
				`processors/${window.application.functionalMap.id}/roi/` +
				`pinwheels/distance_map/`;
			let result = await client.post(url);
			let redirectionUrl = `/data/${result.id}/`;
			window.postMessage({method: 'redirect', info: redirectionUrl}, window.location.origin);
			this.reportFetchSuccess(undefined);
		} catch (error){
			this.reportFetchFailure(error);
		}
	}

}