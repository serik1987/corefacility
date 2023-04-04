import BaseProject from 'corefacility-base/model/entity/Project';

import FunctionalMap from './FunctionalMap';


/**
 * 	This is an improved version of the project class that contains references to the functional maps.
 */
export default class Project extends BaseProject{

	/**
	 * 	Returns list of all maps connected to a given project
	 * 	@async
	 * 	@param {object} searchParams 	the search params to use
	 * 	@return 						EntityPage of all maps satisfying given condition
	 */
	async getMaps(searchParams){
		return await this._getChildEntities(FunctionalMap, searchParams);
	}

}