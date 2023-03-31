import {NotImplementedError} from 'corefacility-base/exceptions/model';
import client from 'corefacility-base/model/HttpClient';
import Module from 'corefacility-base/model/entity/Module';

import ListLoader from './ListLoader';


/**
 * 	Represents list of all installed applications connected to a given entry point.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback} 		on404 				Triggers when no requested resource was found.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	_isLoading, _isError, _error props are nor specified for direct access. Use instead:
 * 		(a) isLoading, isError, error Javascript properties
 * 		(b) reportListFetching, reportFetchSuccess(itemList), reportFetchFailure(error) methods
 * 
 * 	Props for the descendant items:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback} 		onItemSelect 		Triggers when the user selects a given item
 * 
 */
export default class InstalledApplicationListLoader extends ListLoader{

	/**
	 *  Returns a URI for the application list fetching (see documentation for details)
	 */
	get applicationFetchUri(){
		throw new NotImplementedError("get applicationFetchUri");
	}

	/**
	 * 	Processes additional information attached to the application list
	 * 	@param {object}		fetchResult			The information returned by the server.
	 */
	processAttachInformation(fetchResult){
		throw new NotImplementedError('fetchResult');
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
	 * Downloads the entity list from the Web server
	 * @param {object} filter 		Filter options to be applied
	 * 								(These options will be inserted to the query parameters)
	 * @return {Array of Module}	List of modules that were downloaded.
	 */
	async _fetchList(filter){
		let fetchResult = await this.getEntityOr404(() => client.get(this.applicationFetchUri));
		if (fetchResult === null){
			return [];
		}

		this.processAttachInformation(fetchResult);
		return Module.deserialize(fetchResult.module_list, true);
	}

}