import Entity from 'corefacility-base/model/entity/Entity';
import {ReadOnlyField, ReadOnlyDateField} from 'corefacility-base/model/fields';

import OsLogProvider from '../providers/OsLogProvider';


/**
 * 	Represents the operating system log
 */
export default class OsLog extends Entity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Operating system log";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 * 	@static
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new OsLogProvider(OsLog),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 * 	@static
	 *  @return {object} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			'time': new ReadOnlyDateField()
				.setDescription("Log time"),
			'hostname': new ReadOnlyField()
				.setDescription("A host that made the log"),
			'message': new ReadOnlyField()
				.setDescription("Log message"),
		}
	}

}