import BaseFunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import RectangularRoi from './RectangularRoi';
import Pinwheel from './Pinwheel';


/**
 * 	This is an improved version of the functional map that contains ROI and pinwheel centers
 */
export default class FunctionalMap extends BaseFunctionalMap{

	/**
	 * 	Returns the list of all created rectangular ROI
	 * 	@param {object}			searchParams 			Object containing filter params for the list
	 * 	@return {Array of RectangularRoi} 				List of all found ROI
	 */
	async getRectangularRoi(searchParams){
		return await this._getChildEntities(RectangularRoi, searchParams);
	}

	/**
	 * 	Returns the list of all saved pinwheel centers
	 * 	@param {object} 		searchParams 			Search criteria for the pinwheel centers
	 * 	@return {Array of Pinwheel} 					List of all found pinwheel centers
	 */
	async getPinwheelList(searchParams){
		return await this._getChildEntities(Pinwheel, searchParams);
	}

}