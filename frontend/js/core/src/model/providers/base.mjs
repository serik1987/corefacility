import {NotImplementedError} from '../../exceptions/model.mjs';


export default class EntityProvider{

	constructor(entityClass){
		this.entityClass = entityClass;
		this._searchParams = undefined;
	}

	get searchParams(){
        return this._searchParams;
    }

    set searchParams(value){
        if (value instanceof Object){
            this._searchParams = value;
        } else {
            throw new TypeError("HttpRequestProvider.searchParams property can be only object");
        }
    }

	createEntity(entity){
		throw new NotImplementedError('createEntity');
	}

	updateEntity(entity){
		throw new NotImplementedError('updateEntity');
	}

	deleteEntity(entity){
		throw new NotImplementedError('deleteEntity');
	}

	loadEntity(lookup){
		throw new NotImplementedError('loadEntity');
	}

	findEntities(){
		throw new NotImplementedError('findEntities');
	}

	toString(){
		return `[EntityProvider]`;
	}

}