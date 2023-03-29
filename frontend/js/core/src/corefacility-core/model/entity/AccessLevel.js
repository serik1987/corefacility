import Entity from 'corefacility-base/model/entity/Entity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {ReadOnlyField} from 'corefacility-base/model/fields';


/**
 *  The access levels
 */
export default class AccessLevel extends Entity{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Access Level";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [new HttpRequestProvider('access-levels', AccessLevel)];
	}

	/** Returns an object containing propertyName => propertyDescription pairs.
	 *  Each property description is an instance of the EntityField class that tells the entity
	 *  how to get or set a given entity field
	 *  @return {object} field description for all fields
	 */
	static _definePropertyDescription(){
		return {
			type: new ReadOnlyField().setDescription("Level type"),
			alias: new ReadOnlyField().setDescription("Level alias"),
			name: new ReadOnlyField().setDescription("Human-readable level name")
		}
	}

}