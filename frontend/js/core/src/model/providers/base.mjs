import {NotImplementedError} from '../../exceptions/model.mjs';


/** This is a base class for entity providers.
 *  Entity providers exchange the information between the Entities and
 *  sources of information about entity fields
 */
export default class EntityProvider{

	/** Initializes the entity provider
	 *  @param {function} entityClass class of the entity for which the entity provider can be created
	 */
	constructor(entityClass){
		this.entityClass = entityClass;
		this._searchParams = undefined;
	}

	/** Filter parameters.
	 *  When the provider will provide the whole entity list, the list will contain
	 *  only those entities that satisfy these filter conditions.
	 * 	A special property field _parentEntityId defines array of all parent entities.
	 * 	All property fields starting from _parentEntityId are special and MUST be ignored during the
	 * 	search
	 * @return {object} object containing names and values of filter parameters
	 */
	get searchParams(){
        return this._searchParams;
    }

    /** Sets the filter parameters (see get searchParams for details)
     *  @param {object} value Search parameters to be set (e.g., {q: 'user'}).
     */
    set searchParams(value){
        if (value instanceof Object){
            this._searchParams = value;
        } else {
            throw new TypeError("EntityProvider.searchParams property can be only object");
        }
    }

    /** Creates an entity
     *  @async
     *  @param {Entity} entity the entity to be created. The entity is assumed to be in state 'CREATING'
     *  @return {undefined}
     */
	async createEntity(entity){
		throw new NotImplementedError('createEntity');
	}

	/** Updates the entity fields
	 * 	@async
	 *  @param {Entity} entity the entity fields to be updated
	 *  @return {undefined}
	 */
	async updateEntity(entity){
		throw new NotImplementedError('updateEntity');
	}

	/** Removes the entity from the external source
	 * 	@async
	 *  @param {Entity} entity the entity to be removed
	 *  @return {undefined}
	 */
	async deleteEntity(entity){
		throw new NotImplementedError('deleteEntity');
	}

	/** Loads the entity from the external source.
	 * 	@async
	 *  @param {any} lookup any information that may undoubtedly define the entity (i.e., entity ID, slug, etc.)
	 *  @return {Entity} the loaded entity
	 */
	async loadEntity(lookup){
		throw new NotImplementedError('loadEntity');
	}

	/** Finds entities in the external source. The entities will be found only when they satisfy some
	 *  filter conditions mentioned in searchParams field
	 * 	@async
	 *  @generator
	 *  @return {Entity iterator} that can be iterated in the for/of loop. Such iteration must return Entities
	 */
	async findEntities(){
		throw new NotImplementedError('findEntities');
	}

	toString(){
		return `[EntityProvider]`;
	}

}