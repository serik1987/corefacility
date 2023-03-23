import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import EntityState from 'corefacility-base/model/entity/EntityState';


/**
 * Provides an interaction between the Group entity and the corefacility Web server
 */
export default class GroupProvider extends HttpRequestProvider{

	/**
	 *  Creates the group provider
	 * 	@param {function} EntityClass  		The Group class
	 */
	constructor(EntityClass){
		super('groups', EntityClass);
	}

	/** Transforms list of entity response containing in the response body to the list of entities
     *  @param {list[object]} list of objects containing in the output response
     *  @return {list[Entity]} list of Entities found
     */
    _resultToListMapper(responseData){
    	return super._resultToListMapper(responseData)
    		.map(group => {
    			group._state = EntityState.loaded;
    			return group;
    		})
    }

}