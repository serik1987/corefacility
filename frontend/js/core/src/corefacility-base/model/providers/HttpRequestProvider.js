import client from '../HttpClient';
import EntityProvider from './EntityProvider';
import Entity from '../entity/Entity';
import EntityPage from '../EntityPage';
import EntityState from '../entity/EntityState';

/** Provides an interaction between the Entity object and the remote Web server */
export default class HttpRequestProvider extends EntityProvider{

    /** Creates the request provider
     *  @param {string} pathSegment path of the entity retrieval URL located
     *                  between the API version and the entity lookup
     *                  e.g., for url like 'http://corefacility.ru/api/v1/users/serik1987/'
     *                  the path segment will be 'users'
     *                  If the path segment contains IDs of parent entities use :id: placeholder
     *                  to tell the system about it.
     *  @param {function} entityClass a class which the providing entity belongs to
     */
    constructor(pathSegment, entityClass){
    	super(entityClass);
    	this.pathSegment = pathSegment;
    }

    /** Returns URL that will be used for downloading entity list and creating new entity
     *  @return {URL} new URL
     */
    _getEntityListUrl(){
        let origin = window.SETTINGS.origin || window.origin;
        let apiVersion = window.SETTINGS.client_version;
        let url = `${origin}/api/${apiVersion}/${this.pathSegment}/`;
        if (typeof this._searchParams === "object" && "_parentIdList" in this.searchParams){
            for (let parentId of this.searchParams._parentIdList){
                url = url.replace(":id:", parentId);
            }
        }
        return new URL(url);
    }

    /** Returns URL that will be used for searching a given entity.
     *  All search params (see help on EntityProvider.searchParams) will be transformed
     *  to URL request params. For example if you set search params like:
     *      provider.searchParams = {q: "Vanya"}
     *  the url will be:
     *      http://corefacility/ru/api/v1/path/to/entity/list/?q=Vanya
     * @return {URL} the URL that will give you list of entities satisfying filter conditions
     */
    _getEntitySearchUrl(searchParams){
        let url = this._getEntityListUrl();
        for (let name in searchParams){
            if (name[0] !== "_"){
                url.searchParams.append(name.toString(), searchParams[name].toString());
            }
        }
        return url;
    }

    /** Returns URL that will be used to reading, modification and delete single entities
     *  @param {string|int} lookup The entity identification (either entity ID or entity alias)
     *                      that will be substituted to the request
     *  @return {URL} the URL that will be used to do the entity CRUD action
     */
    _getEntityDetailUrl(lookup){
        let url = this._getEntityListUrl();
        if (lookup instanceof Entity){
            lookup = lookup.id;
        }
        url.pathname += `${lookup}/`;
        return url;
    }

    /** Creates new entity
     *  @async
     *  @param {Entity} the entity to be created. The entity is assumed to be in state CREATING
     *  @return {Entity} the created entity
     */
    createEntity(entity){
        let url = this._getEntityListUrl();
        let requestData = Object.assign({}, entity._entityFields);
        delete requestData['id'];
        return client.post(url, requestData)
            .then(responseData => {
                Object.assign(entity._entityFields, responseData);
                return entity;
            });
    }

    /** Modifies the entity
     *  @async
     *  @param {Entity} entity the entity to modify
     *  @return {undefined}
     */
    updateEntity(entity){
        let url = this._getEntityDetailUrl(entity);
        let inputData = {};
        for (let property of entity._propertiesChanged){
            inputData[property] = entity._entityFields[property];
        }
        return client.patch(url, inputData)
            .then(responseData => {
                Object.assign(entity._entityFields, responseData);
            });
    }

    /** Removes the entity
     *  @async
     *  @param {Entity} entity the entity to remove
     *  @return {undefined}
     */
    deleteEntity(entity){
    	let url = this._getEntityDetailUrl(entity);
        return client.delete(url);
    }

    /** Downloads the entity from the Web server
     *  @async
     *  @param {string|int} lookup value that undoubtedly identifies the entity
     *      the value could be either integer entity ID or string-like entity alias
     *  @return {Entity} the downloaded entity
     */
    loadEntity(lookup){
        let url = this._getEntityDetailUrl(lookup);
        return client.get(url)
            .then(responseData => {
                let entity = new this.entityClass();
                Object.assign(entity._entityFields, responseData);
                return entity;
            });
    }

    /** Finds entities satisfying given filter conditions. The conditions are
     *      saved to searchParams field
     *  @async
     *  @return {EntityPage|array[Entity]} if the entity find response was paginated,
     *                                     returns a special object that can be used
     *                                     to navigate among different pages
     *                                     (see src/entity/EntityPage.mjs).
     *                                     Otherwise, returns a simple array of entities
     */
    findEntities(){
        let url = this._getEntitySearchUrl(this.searchParams);
        return client.get(url)
            .then(responseData => {
                if ("count" in responseData && "next" in responseData && "previous" in responseData){
                    return new EntityPage({
                        "count": responseData.count,
                        "previous": responseData.previous,
                        "next": responseData.next,
                        "entities": this._resultToListMapper(responseData.results),
                        "resultToListMapper": this._resultToListMapper.bind(this),
                    });
                } else {
                    return this._resultToListMapper(responseData);
                }
            });
    }

    toString(){
    	return `[${this.pathSegment.charAt(0).toUpperCase()}${this.pathSegment.slice(1)}Provider]`;
    }

    /** Transforms list of entity response containing in the response body to the list of entities
     *  @param {list[object]} list of objects containing in the output response
     *  @return {list[Entity]} list of Entities found
     */
    _resultToListMapper(responseData){
        return responseData.map(entityInfo => {
            let entity = new this.entityClass();
            Object.assign(entity._entityFields, entityInfo);
            entity._state = EntityState.found;
            return entity;
        });
    }

    getObjectFromResult(result){
        return this._resultToListMapper([result])[0];
    }

}
