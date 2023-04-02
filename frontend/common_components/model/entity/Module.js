import Entity from './Entity';
import HttpRequestProvider from '../providers/HttpRequestProvider';
import {ReadOnlyField, BooleanField} from '../fields';
import EntryPoint from './EntryPoint';
import EntityState from './EntityState';


export default class Module extends Entity{

	/** Returns instance that is a model of a currently loading application
	 */
	static getIdentity(){
		let identity = new this();
		identity._entityFields = window.SETTINGS.app;
		identity._state = EntityState.loaded;
		return identity;
	}

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Corefacility Module";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider("settings", this),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			"uuid": new ReadOnlyField()
				.setDescription("Universally Unique IDentifier"),
			"alias": new ReadOnlyField()
				.setDescription("Alias"),
			"name": new ReadOnlyField()
				.setDescription("Name"),
			"html_code": new ReadOnlyField()
				.setDescription("HTML code"),
			"node_number": new ReadOnlyField()
				.setDescription("Number of entry points"),
			"is_enabled": new BooleanField()
				.setDescription("Is module enabled"),
			"pseudomodule_identity": new ReadOnlyField()
				.setDescription("Identity of the pseudo-module"),
		};
	}

	/** Returns the root module
	 * 	@async
	 * 	@return {Module} the root module
	 */
	static async getRootModule(){
		for (let corefacilityModule of await this.find({entry_point: 0})){
			return corefacilityModule;
		}
		throw new Error("No root module found!");
	}

	/** Modules doesn't have IDs - they have UUIDs */
	get id(){
		return this.uuid;
	}

	toString(){
		let string = `${this.name}\n`;
		string += this._getAllPropertiesString()
		return string;
	}

	/** Retrieves all entry points belonging to this module.
	 * 
	 * 	@async
	 * 	@return {array of EntryPoint} list of all entry points
	 */
	findEntryPoints(){
		return this._getChildEntities(EntryPoint, {_parentIdList: [this.uuid]});
	}

}