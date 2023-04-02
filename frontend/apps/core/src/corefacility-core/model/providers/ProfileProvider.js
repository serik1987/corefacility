import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import EntityState from 'corefacility-base/model/entity/EntityState';



/* Provides interaction between the Profile object and the remote Web server */
export default class ProfileProvider extends HttpRequestProvider{

	/** Creates the request provider
     *  @param {function} entityClass a class which the providing entity belongs to
     */
    constructor(entityClass){
    	super('profile', entityClass);
    }

    /**
     * Does nothing because profile list feature is not supported
     */
    _getEntityListUrl(){
    	throw new Error("List loading is not supported in the ProfileProvider");
    }


    /**
     * Does nothing because profile liswt feature is not supported
     * @param {string} searchParams 		useless
     */
    _getEntitySearchUrl(searchParams){
    	throw new Error("List loading is not supported in the ProfileProvider");
    }

    /**
     * Finds a URL for calculation of the current user profile
     * @param {string|int} lookup 			useless
     * @return {URL} 						the URL to be used for profile retrieval and update
     */
    _getEntityDetailUrl(){
    	return super._getEntityListUrl();
    }

    /** Transforms list of entity response containing in the response body to the list of entities
     *  @param {list[object]} list of objects containing in the output response
     *  @return {list[Entity]} list of Entities found
     */
    _resultToListMapper(responseData){
        throw new Error("List wrapping is not supported in the ProfileProvider");
    }

    /**
     * Transforms the HTTP response output data to a single object
     * @param {object} result the HTTP response data that represents one given object
     * @return {Entity} the recovered entity
     */
    getObjectFromResult(result){
        let profile = super._resultToListMapper([result])[0];
        profile._state = EntityState.loaded;
        return profile;
    }

    /** Creates new entity
     *  @async
     *  @param {Entity} the entity to be created. The entity is assumed to be in state CREATING
     *  @return {Entity} the created entity
     */
    createEntity(entity){
        throw new Error("You can't create your another profile");
    }

    /** Removes the entity
     *  @async
     *  @param {Entity} entity the entity to remove
     *  @return {undefined}
     */
    deleteEntity(entity){
    	throw new Error("You can't delete your own profile");
    }

}