import {NotImplementedError, EntityPropertyError, EntityStateError, ReadOnlyPropertyError}
    from 'corefacility-base/exceptions/model';
import EntityState from './EntityState';


/** This is a base class for all entities
 *  The Entity is some client-side object (e.g., user, project, data file)
 *  that the client user can or can't read, save, modify or delete.
 * 
 *  The entities may have one or several external entity sources. The entity
 *  operations are provided as exchange of information between entities and
 *  their external sources.
 * 
 *  Each entity has one or several entity fields, Such fields can be 
 *  modified as simple Javascript properties.
 *  Example: get user ID:      some_user.id
 *           set user E-mail:  some_user.email = 'sergei.kozhukhov@ihna.ru'
 *  When the entity field is read-only, you are not allowed to modify it, 
 *  in this case ReadOnlyPropertyError will be thrown
 */
export default class Entity{

	/** Creates new entity.
	 *  The constructor called outside the class is used to create the entity
	 *  that have never been saved to any of the external sources.
	 *  Entity creating doesn't imply its immediately saving to the external
	 *  source
	 *  @param entityInfo values of the entity fields that will be automatically
	 *                    assigned during the entity create
	 */
	constructor(entityInfo){
		this._entityFields = {id: null};
		this._state = 'creating';
		this._tag = undefined;
		this._propertiesChanged = new Set();
		this._parentIdList = [];
		this._defineProperties();
		if (entityInfo !== null && entityInfo !== undefined){
			this._setInitialProperties(entityInfo);
		}
	}

	/** The entity ID or null if the entity was not created in the external source.
	 *  Each entity has unique entity ID that can be used to distinguish
	 *  one entity from another one and point exactly to this given entity.
	 *  Any entity
	 */
	get id(){
		return this._entityFields.id;
	}

	/** Throws an exception indicating that the entity ID is read-only */
	set id(value){
		throw new ReadOnlyPropertyError(this._entityName, "id");
	}

	/** The entity tag is small value of any type that can be assigned by the view.
	 * 	The entity tags are used separated different entity in some groups.
	 */
	get tag(){
		return this._tag;
	}

	set tag(value){
		this._tag = value;
	}

	/** Read-only property indicating the entity state. The property equals to one
	 *  of the following values:
	 *  'creating' the entity was initialized on the client side but was not sent
	 *  to the remote server to its create. Only create() operation is allowed here.
	 *  'saved' the entity has been recently save due to either create() or update().
	 *  All operations except create() are allowed here
	 *  'loaded' the entity has been recently downloaded from the server.
	 *  'changed' the entity was modified but the changes were not saved in the external
	 *  sources. If your entity has 'changed' state this means that you have to call
	 *  the update() method. Otherwise, your changes may be lost.
	 *  'deleted' the entity has been removed from the external Web server
	 *  'pending' the last entity operation returned the promise that has not been
	 *  resolved. In this case any entity operatings as well as its modification is not allowed.
	 *  If you see the entity in the pending state, it means that you forgot to put the
	 *  'await keyword somewhere'.
	 */
	get state(){
		return this._state;
	}

	/** Creates the entity on the remote service
	 *  @async
	 *  @return {undefined}
	 */
	async create(){
		if (this._state !== EntityState.creating){
			throw new EntityStateError(this._state, 'create');
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => {
				provider.searchParams = {_parentIdList: this._parentIdList};
				return provider.createEntity(this)
			});
		try{
			await Promise.all(promises);
			this._state = EntityState.saved;
		} catch (e){
			this._state = EntityState.creating;
			throw e;
		}
	}

	/** This is a static method that downloads entity with a given ID or alias
	 *  @async
	 *  @static
	 *  @param {int|string} lookup the entity ID or alias
	 *  @return {Entity} the entity to be returned
	 */
	static async get(lookup){
		let searchProvider = this._entityProviders[this.SEARCH_PROVIDER_INDEX];
		let entity = await searchProvider.loadEntity(lookup);
		entity._state = "loaded";
		return entity;
	}

	/** Returns a copy of the entity downloaded from the server
	 *  @async
	 *  @return {Entity} the entity copy
	 */
	async reload(){
		return this.constructor.get(this.id);
	}

	/** Saves all entity changes to the hard disk.
	 *  @async
	 *  @return {undefined}
	 */
	async update(){
		if (this._state === EntityState.loaded || this._state === EntityState.saved){
			return;
		}
		let previousState = this._state;
		if (this._state !== EntityState.changed){
			throw new EntityStateError(this._state, "update");
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => {
				provider.searchParams = {_parentidList: this._parentIdList};
				return provider.updateEntity(this);
			});
		try{
			await Promise.all(promises);
			this._state = EntityState.saved;
			this._propertiesChanged.clear();
		} catch (e){
			this._state = previousState;
			throw e;
		}
	}

	/**
	 *  Deletes an object with ?force parameter
	 * 	@async
	 */
	async forceDelete(){
		for (let provider of this.constructor._entityProviders){
			provider.forceDelete = true;
		}
		try{
			await this.delete();
		} catch (error){
			throw error;
		} finally {
			for (let provider of this.constructor._entityProviders){
				provider.forceDelete = false;
			}
		}
	}

	/** Deletes the entity from the external source
	 *  @async
	 *  @return {undefined}
	 */
	async delete(){
		let previousState = this._state;
		if (this._state === EntityState.creating || this._state === EntityState.deleted || this._state === EntityState.pending){
			throw new EntityStateError(this._state, "delete");
		}
		this._state = EntityState.pending;
		let promises = this.constructor._entityProviders
			.map(provider => {
				provider.searchParams = {_parentIdList: this._parentIdList};
				return provider.deleteEntity(this);
			});
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

	/** Finds all entities satisfying given conditions
	 * 	@async
	 *  @static
	 *  @param {object} searchParams. The entity search params depending on the given entity.
	 *  @return {EntityPage|list[Entity]}
	 * 		The output result depends on whether the response from the Web server is paginated or not.
	 * 		If the response is paginated, it means that the Web server sends only small pieces of the 
	 * 		entity lists. Such a piece is called 'entity page'. In this case the function returns a single
	 * 		entity page. The entity page allows to read all entities containing in the page as well as
	 * 		navigate between pages.
	 * 		If the response is not paginated, it means that the Web server will send the whole list of
	 * 		entity. Such a list will be transformed to the Javascript's array of the entity objects and
	 * 		returned here.
	 */
	static async find(searchParams){
		let searchProvider = this._entityProviders[this.SEARCH_PROVIDER_INDEX];
		if (!searchParams){
			searchParams = {};
		}
		searchProvider.searchParams = searchParams;
		let entities = await searchProvider.findEntities();
		if (entities instanceof Array){
			entities.map(entity => { return entity._state = EntityState.found; });
		}
		return entities;
	}

	toString(){
		let string = `${this.constructor._entityName} (ID = ${this.id}) [${this.state.toUpperCase()}]\n`;
		string += this._getAllPropertiesString()
		return string;
	}

	_getAllPropertiesString(){
		let propertyDescription = this.constructor._propertyDescription;
		let string = "----------------------------------------------------------\n";

		for (let field in propertyDescription){
			string += `${propertyDescription[field].description} [${field}]: ${this[field]}\n`;
		}
		
		return string;
	}

	/** Checks whether given entity field is required or not/
	 *  If the field is required, you can't create the entity using the create() method until
	 *  some value will be set to the field
	 *  @static
	 *  @param {string} fieldName name of the field to check
	 *  @return {boolean} true if the field is required, false otherwise
	 */
	static isFieldRequired(fieldName){
		if (fieldName === "id"){
			return false;
		} else {
			return this._propertyDescription[fieldName].required;
		}
	}

	/** Applies standard Javascript's Object.defineProperty routine that allows you to
	 *  deal with entity fields as with simple Entity object's properties.
	 * 	@return {undefined}
	 */
	_defineProperties(){
		let propertyDescription = this.constructor._propertyDescription;
		for (let propertyName in propertyDescription){
			Object.defineProperty(this, propertyName, {
				get() {
					if (propertyName in this._entityFields){
						return propertyDescription[propertyName].correct(this, propertyName, this._entityFields[propertyName]);
					} else {
						return propertyDescription[propertyName].default;
					}
				},
				set(value){
					if (this._state === "deleted" || this._state === "pending" || this._state === "found"){
						throw new EntityStateError(this._state, "property change");
					}
					let internalValue;
					if (value === undefined){
						internalValue = undefined;
					} else {
						internalValue = propertyDescription[propertyName].proofread(this, propertyName, value);
					}
					if (internalValue !== undefined){
						this._entityFields[propertyName] = internalValue;
					} else if (propertyName in this._entityFields){
						delete this._entityFields[propertyName];
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

	/** The function was invoked once and used to set initial values to the entity fields
	 *  @param {entityInfo} the initial values to the entity fields passed as constructor arguments
	 *  @return {undefined}
	 */
	_setInitialProperties(entityInfo){
		for (let propertyName in entityInfo){
			if (!(propertyName in this.constructor._propertyDescription)){
				throw new EntityPropertyError(this.constructor.name, propertyName);
			}
			this[propertyName] = entityInfo[propertyName];
		}
	}

	/** Returns the child entities of this current entity.
	 * 	Child entities are such entities which seek is impossible without telling the
	 * 	parent entity ID
	 * 	@async
	 * 	@param {function} childEntityClass that class belonging to the child entity
	 * 	@return {iterator} the iterable over all child entities
	 */
	async _getChildEntities(childEntityClass, searchParams){
		if (!searchParams){
			searchParams = {};
		}
		if (!("_parentIdList" in searchParams)){
			searchParams._parentIdList = [...this._parentIdList, this.id];
		}
		searchParams._parent = this;
		return childEntityClass.find(searchParams);
	}

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		throw new NotImplementedError('static get _entityName');
	}

	/**
	 *  Returns the very first (search) provider
	 */
	static get searchEntityProvider(){
		return this._entityProviders[this.SEARCH_PROVIDER_INDEX];
	}

	/** Returns the list of all entity providers.
	 *  Each entity provider should be associated with a certain external source where entities
	 *  contains and provides entity save or retrieve only for this sources. When you create, update
	 * 	or delete the entity, all providers in the list will be asked to create, update or delete the entity.
	 *  @static
	 * 	@return {list[EntityProvider]} list of entity provider objects
	 */
	static get _entityProviders(){
	    if (!this.hasOwnProperty('__internalEntityProviders')){
	        this.__internalEntityProviders = this._defineEntityProviders();
	    }
	    return this.__internalEntityProviders;
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @abstract
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		throw new NotImplementedError('static _defineEntityProviders');
	}

	/** Returns an object containing propertyName => propertyDescription pairs.
	 *  Each property description is an instance of the EntityField class that tells the entity
	 *  how to get or set a given entity field
	 *  @return {object} field description for all fields
	 */
	static get _propertyDescription(){
		if (!this.hasOwnProperty('__internalPropertyDescription')){
			this.__internalPropertyDescription = this._definePropertyDescription();
		}
		return this.__internalPropertyDescription;
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @abstract
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		throw new NotImplementedError("static _definePropertyDescription");
	}

}


/** Index of the entity provider in the EntityClass._entityProviders array
 *  that will be used for get() and find() functions
 */
Entity.SEARCH_PROVIDER_INDEX = 0;