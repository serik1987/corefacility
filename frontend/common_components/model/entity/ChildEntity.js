import Entity from './Entity';


/** Represents an entity that is a child of another entity.
 * 
 * 	Child entities are such entities that can't be retrieved without insert of the parent ID to the API path
 *  An example of the child entity is entry point: to reveal the entry point you must put the module UUID to the
 *  entry point path.
 *
 *  User's group is not an example of the child entity because user groups can be reveal without putting the user ID
 *  to the API path
 */
export default class ChildEntity extends Entity{

    /** Creates new entity.
     *  The constructor called outside the class is used to create the entity
     *  that have never been saved to any of the external sources.
     *  Entity creating doesn't imply its immediately saving to the external
     *  source
     *  @param {object} entityInfo values of the entity fields that will be automatically
     *                    assigned during the entity create
     *  @param {Entity} parentEntity the entity this child entity belongs to
     */
    constructor(entityInfo, parentEntity = null){
        super(entityInfo);
        this._entityFields.__parent = null;
        if (parentEntity){
            this._entityFields.__parent = parentEntity;
            this._parentIdList = [...parentEntity._parentIdList, parentEntity.id];
        }
    }

    /**
     * The parent entity
     */
    get parent(){
        return this._entityFields.__parent;
    }

    /** Finds all entities satisfying given conditions
     *  @async
     *  @static
     *  @param {object} searchParams. The entity search params depending on the given entity.
     *  @return {EntityPage|list[Entity]}
     *      The output result depends on whether the response from the Web server is paginated or not.
     *      If the response is paginated, it means that the Web server sends only small pieces of the 
     *      entity lists. Such a piece is called 'entity page'. In this case the function returns a single
     *      entity page. The entity page allows to read all entities containing in the page as well as
     *      navigate between pages.
     *      If the response is not paginated, it means that the Web server will send the whole list of
     *      entity. Such a list will be transformed to the Javascript's array of the entity objects and
     *      returned here.
     */
    static async find(searchParams){
        let entities = await Entity.find.bind(this)(searchParams);
        if (entities instanceof Array){
            entities.map(entity => ChildEntity.__createChildRelations(entity, searchParams));
        } else if ("_entityList" in entities){
            entities._entityList.map(entity => ChildEntity.__createChildRelations(entity, searchParams));
        }
        return entities;
    }

    /**
     *  Creates relations between child entity and the parent
     *  @static
     *  @param {ChildEntity} entity     the child entity which relations must be established
     *  @param {Object} searchParams    search params that were used to retrieve this particular child entity
     */
    static __createChildRelations(entity, searchParams){
        entity._parentIdList = searchParams._parentIdList;
        if ('_parent' in searchParams){
            entity._entityFields.__parent = searchParams._parent;
        }
        return null;
    }

    /**
     *  Recovers the entity from its serialized information
     *  @static
     *  @param {object|array} info the serialized information about the entity (many = false), or
     *          array of such objects (many = true).
     *  @param {boolean} many true to deserialize list of entities, false to deserialize single entity
     *  @return {Entity|array of Entity} the entity itself (many = false) or array of entities (many = true)
     */
    static deserialize(info, many=false){
        if (!('parent' in info)){
            throw new Error("When you deserialize the child entity, its first argument must contain the parent field");
        }
        let parentEntity = info.parent;
        delete info.parent;
        let childEntity = super.deserialize(info, many);
        childEntity._entityFields.__parent = parentEntity;
        return childEntity;
    }

    /**
     *  Transforms entity to its serialized state. The entity can be recovered from its serialized state using the
     *  deserialize() method
     *  @return {object} the serialized state of the entity
     */
    serialize(){
        let serializedData = super.serialize();
        serializedData.parent = serializedData.__parent;
        delete serializedData.__parent;
        return serializedData;
    }

}