import client from 'corefacility-base/model/HttpClient';
import EntityPage from 'corefacility-base/model/EntityPage';
import RectangularRoi from 'corefacility-roi/model/RectangularRoi';

import FunctionalMapDrawingEditor from './FunctionalMapDrawingEditor';
import RectangularRoiGraphicList from './RectangularRoiGraphicList';
import RectangularRoiList from './RectangularRoiList';


/**
 * 	Connects the functional map drawer to the list of the rectangular ROI
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
 * 	@param {callback} onItemAdd 				This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class RectangularRoiEditor extends FunctionalMapDrawingEditor{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return RectangularRoi;
	}

	/**
     *  Returns the graphic item list
     */
    get graphicItemListComponent(){
        return RectangularRoiGraphicList;
    }

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return RectangularRoiList;
	}

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the )
	 */
	async _fetchList(filter){
		if (window.application.functionalMap){
			return await window.application.functionalMap.getRectangularRoi(filter);
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
					onItemAdd={this.handleItemAdd}
					onItemSelect={this.handleSelectItem}
					onItemRemove={this.handleItemRemove}
					onApplyRoi={roi => this.applyRoi(roi)}
				/>);
	}

	/**
	 * 	Cuts the map using the ROI
	 * 	@async
	 * 	@param {RectangularRoi} roi 					ROI to apply
	 */
	async applyRoi(roi){
		try{
			this.reportListFetching();
			let apiVersion = window.SETTINGS.client_version;
			let projectId = window.application.project.id;
			let mapId = window.application.functionalMap.id;
			let url = `/api/${apiVersion}/core/projects/${projectId}/imaging/processors/${mapId}` +
				`/roi/rectangular/${roi.id}/cut_map/`;
			let result = await client.post(url, {});
			let redirectionUrl = `/data/${result.id}/`;
			window.postMessage({method: 'redirect', info: redirectionUrl}, window.location.origin);
			this.reportFetchSuccess(undefined);
		} catch (error){
			this.reportFetchFailure(error);
		}
	}

}