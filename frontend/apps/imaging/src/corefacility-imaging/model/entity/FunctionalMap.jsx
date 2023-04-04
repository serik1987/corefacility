import ChildEntity from 'corefacility-base/model/entity/ChildEntity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';


/**
 * 	Represents a single functional map.
 */
export default class FunctionalMap extends ChildEntity{

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 * 	@static
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider('core/projects/:id:/imaging/data', FunctionalMap),
		];
	}


}