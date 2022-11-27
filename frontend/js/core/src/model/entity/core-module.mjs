import {BooleanField, IntegerField} from '../fields/fields.mjs';
import Module from './module.mjs';


export default class CoreModule extends Module{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Core functionality";
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			is_user_can_change_password: new BooleanField()
				.setDescription("Can user change its password?"),
			max_password_symbols: new IntegerField()
				.setDescription("Maximum password symbols")
				.setMinValue(6),
		}
	}

}