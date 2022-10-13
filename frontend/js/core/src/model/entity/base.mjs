import {NotImplementedError, EntityPropertyError, EntityStateError, ReadOnlyPropertyError} from '../../exceptions/model.mjs';
import EntityPage from './page.mjs';
import EntityState from './entity-state.mjs';


export default class Entity{

	constructor(entityInfo){
		this._entityFields = {id: null};
		this._state = 'creating';
		this._propertiesChanged = new Set();
		this._defineProperties();
		if (entityInfo !== null && entityInfo !== undefined){
			this._setInitialProperties(entityInfo);
		}
		this.constructor._entityProviders;
	}

	get id(){
		return this._entityFields.id;
	}

	set id(value){
		throw new ReadOnlyPropertyError(this._entityName, "id");
	}

	get state(){
		return this._state;
	}

	async create(){
		if (this._state != EntityState.creating){
			throw new EntityStateError(this._state, 'create');
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => provider.createEntity(this));
		try{
			await Promise.all(promises);
			this._state = EntityState.saved;
		} catch (e){
			this._state = EntityState.creating;
			throw e;
		}
	}

	static async get(lookup){
		let searchProvider = this._entityProviders[this.SEARCH_PROVIDER_INDEX];
		let entity = await searchProvider.loadEntity(lookup);
		entity._state = "loaded";
		return entity;
	}

	async reload(){
		return this.constructor.get(this.id);
	}

	async update(partial=true){
		if (this._state === EntityState.loaded || this._state === EntityState.saved){
			return;
		}
		let previousState = this._state;
		if (this._state !== EntityState.changed){
			throw new EntityStateError(this._state, "update");
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => provider.updateEntity(this, partial));
		try{
			await Promise.all(promises);
			this._state = EntityState.saved;
			this._propertiesChanged.clear();
		} catch (e){
			this._state = previousState;
			throw e;
		}
	}

	async delete(){
		let previousState = this._state;
		if (this._state === EntityState.creating || this._state === EntityState.deleted || this._state === EntityState.pending){
			throw new EntityStateError(this._state, "delete");
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => provider.deleteEntity(this));
		try{
			await Promise.all(promises);
			this._state = EntityState.deleted;
			this._propertiesChanged.clear();
			this._entityFields.id = null;
		} catch (e){
			this._state = previousState;
			throw e;
		}
	}

	static async find(searchParams){
		let searchProvider = this._entityProviders[this.SEARCH_PROVIDER_INDEX];
		if (!searchParams){
			searchParams = {};
		}
		searchProvider.searchParams = searchParams;
		let entities = await searchProvider.findEntities();
		if (entities instanceof EntityPage){
			entities._entityList.map(entity => { entity._state = "found"; });
		} else {
			entities.map(entity => { entity._state = "found"; });
		}
		return entities;
	}

	toString(){
		let string = `${this.constructor._entityName} (ID = ${this.id}) [${this.state.toUpperCase()}]\n` + 
			"----------------------------------------------------------\n";
		let propertyDescription = this.constructor._propertyDescription;
		for (let field in propertyDescription){
			string += `${propertyDescription[field].description} [${field}]: ${this[field]}\n`;
		}
		return string;
	}

	static isFieldRequired(fieldName){
		if (fieldName === "id"){
			return false;
		} else {
			return this._propertyDescription[fieldName].required;
		}
	}

	_defineProperties(){
		let propertyDescription = this.constructor._propertyDescription;
		for (let propertyName in propertyDescription){
			Object.defineProperty(this, propertyName, {
				get() {
					if (propertyName in this._entityFields){
						return propertyDescription[propertyName].correct(this._entityFields[propertyName]);
					} else {
						return propertyDescription[propertyName].default;
					}
				},
				set(value){
					if (this._state === "deleted" || this._state === "pending" || this._state === "found"){
						throw new EntityStateError(this._state, "property change");
					}
					let internalValue = propertyDescription[propertyName].proofread(this._entityName, propertyName, value);
					if (internalValue !== undefined){
						this._entityFields[propertyName] = internalValue;
					}
					if (this._state !== "creating"){
						this._state = "changed";
					}
					this._propertiesChanged.add(propertyName);
				},
				enumerable: true,
				configurable: false
			});
		}
		Object.preventExtensions(this);
	}

	_setInitialProperties(entityInfo){
		for (let propertyName in entityInfo){
			if (!(propertyName in this.constructor._propertyDescription)){
				throw new EntityPropertyError(this.constructor.name, propertyName);
			}
			this[propertyName] = entityInfo[propertyName];
		}
	}

	static get _entityName(){
		throw new NotImplementedError('static get _entityName');
	}

	static get _entityProviders(){
		if (this.__internalEntityProviders === undefined){
			this.__internalEntityProviders = this._defineEntityProviders();
		}
		return this.__internalEntityProviders;
	}

	static _defineEntityProviders(){
		throw new NotImplementedError('static _defineEntityProviders');
	}

	static get _propertyDescription(){
		if (this.__internalPropertyDescription === undefined){
			this.__internalPropertyDescription = this._definePropertyDescription();
		}
		return this.__internalPropertyDescription;
	}

	static _definePropertyDescription(){
		throw new NotImplementedError("static _definePropertyDescription");
	}

}

Entity.SEARCH_PROVIDER_INDEX = 0;