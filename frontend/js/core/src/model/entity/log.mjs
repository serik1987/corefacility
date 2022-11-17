import HttpRequestProvider from '../providers/http-request.mjs';
import {ReadOnlyField, ReadOnlyDateField} from '../fields/fields.mjs';
import RelatedField from '../fields/related-field.mjs';
import Entity from './base.mjs';
import User from './user.mjs';
import LogRecord from './log-record.mjs';


/** Viewing logs
 */
export default class Log extends Entity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Log"
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @abstract
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider("logs", Log),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @abstract
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			"ip_address": new ReadOnlyField()
				.setDescription("IP address"),
			"operation_description": new ReadOnlyField()
				.setDescription("Operation description"),
			"request_date": new ReadOnlyDateField()
				.setDescription("Request date"),
			"request_method": new ReadOnlyField()
				.setDescription("Request method"),
			"response_status": new ReadOnlyField()
				.setDescription("Response status"),
			"user": new RelatedField(User)
				.setDescription("User"),
			"log_address": new ReadOnlyField()
				.setDescription("Request address"),
			"request_body": new ReadOnlyField()
				.setDescription("Request body"),
			"response_body": new ReadOnlyField()
				.setDescription("Response body"),
			"records": new RelatedField(LogRecord, true)
				.setDescription("Log records"),
		}
	}

}
