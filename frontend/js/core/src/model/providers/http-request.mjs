import client from './http-client.mjs';
import EntityProvider from './base.mjs';
import Entity from '../entity/base.mjs';
import EntityPage from '../entity/page.mjs';

export default class HttpRequestProvider extends EntityProvider{

    constructor(pathSegment, entityClass){
    	super(entityClass);
    	this.pathSegment = pathSegment;
    }

    _getEntityListUrl(){
        let apiVersion = window.SETTINGS.client_version;
        return new URL(`${this.constructor.ORIGIN}/api/${apiVersion}/${this.pathSegment}/`);
    }

    _getEntitySearchUrl(searchParams){
        let url = this._getEntityListUrl();
        searchParams = searchParams || {};
        for (let name in searchParams){
            url.searchParams.append(name.toString(), searchParams[name].toString());
        }
        return url;
    }

    _getEntityDetailUrl(lookup){
        let url = this._getEntityListUrl();
        if (lookup instanceof Entity){
            lookup = lookup.id;
        }
        url.pathname += `${lookup}/`;
        return url;
    }

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

    updateEntity(entity, partial=true){
        let method = partial ? 'PATCH' : 'PUT';
        let url = this._getEntityDetailUrl(entity);
        let inputData = {};
        for (let property of entity._propertiesChanged){
            inputData[property] = entity._entityFields[property];
        }
        return client.request(url, method, inputData)
            .then(responseData => {
                entity._entityFields = {};
                Object.assign(entity._entityFields, responseData);
            });
    }

    deleteEntity(entity){
    	let url = this._getEntityDetailUrl(entity);
        return client.delete(url);
    }

    loadEntity(lookup){
        let url = this._getEntityDetailUrl(lookup);
        return client.get(url)
            .then(responseData => {
                let entity = new this.entityClass();
                Object.assign(entity._entityFields, responseData);
                return entity;
            });
    }

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

    _resultToListMapper(responseData){
        return responseData.map(entityInfo => {
            let entity = new this.entityClass();
            Object.assign(entity._entityFields, entityInfo);
            return entity;
        });
    }

}

HttpRequestProvider.ORIGIN = globalThis.ORIGIN || window.origin;