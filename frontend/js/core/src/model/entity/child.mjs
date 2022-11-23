import Entity from './base.mjs';


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
            entities.map(entity => { return entity._parentIdList = searchParams._parentIdList});
        } else if ("_entityList" in entities){
            entities._entityList.map(entity => {return entity._parentIdList = searchParams.parentIdList});
        }
        return entities;
    }

}