import HttpRequestProvider from '../providers/HttpRequestProvider';
import ReadOnlyField from '../fields';
import ChildEntity from './ChildEntity';


/** Represents an entry point
 */
export default class EntryPoint extends ChildEntity{

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider("settings/:id:/entry-points", EntryPoint),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			"alias": new ReadOnlyField()
				.setDescription("Alias"),
			"name": new ReadOnlyField()
				.setDescription("Human-readable name"),
		}
	}

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Entry Point";
	}

}