import Entity from './base.mjs';
import {ReadOnlyDateField, ReadOnlyField} from '../fields/fields.mjs';


/** Viewing records related to a given log.
 */
export default class LogRecord extends Entity{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Log record";
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			"record_time": new ReadOnlyDateField()
				.setDescription("Record time"),
			"level": new ReadOnlyField()
				.setDescription("Severity level"),
			"message": new ReadOnlyField()
				.setDescription("Message"),
		};
	}

}