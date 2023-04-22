import BaseFunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import RectangularRoi from './RectangularRoi';


/**
 * 	This is an improved version of the functional map that contains ROI and pinwheel centers
 */
export default class FunctionalMap extends BaseFunctionalMap{

	async getRectangularRoi(searchParams){
		return await this._getChildEntities(RectangularRoi, searchParams);
	}

}