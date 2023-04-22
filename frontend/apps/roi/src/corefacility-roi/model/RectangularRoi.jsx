import ChildEntity from 'corefacility-base/model/entity/ChildEntity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {IntegerField} from 'corefacility-base/model/fields';
import EntityState from 'corefacility-base/model/entity/EntityState';



export default class RectangularRoi extends ChildEntity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Rectangular ROI";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 * 	@static
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider('core/projects/:id:/imaging/processors/:id:/roi/rectangular', RectangularRoi)
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair 
	 * 	@static
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			left: new IntegerField()
				.setMinValue(0)
				.setRequired(true)
				.setDescription("Left side"),
			top: new IntegerField()
				.setMinValue(0)
				.setRequired(true)
				.setDescription("Top side"),
			right: new IntegerField()
				.setMinValue(0)
				.setRequired(true)
				.setDescription("Right side"),
			bottom: new IntegerField()
				.setMinValue(0)
				.setRequired(true)
				.setDescription("bottom side"),
		}
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
        let entities = await super.find(searchParams);
        entities.map(entity => entity._state = EntityState.loaded);
        return entities;
    }

}