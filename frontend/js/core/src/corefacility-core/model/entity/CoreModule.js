import {BooleanField, IntegerField} from 'corefacility-base/model/fields';
import Module from 'corefacility-base/model/entity/Module';
import DurationField from 'corefacility-base/model/fields/DurationField';


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
			auth_token_lifetime: new DurationField()
				.setDescription("Authorization token lifetime"),
			is_user_can_change_password: new BooleanField()
				.setDescription("Can user change its password?"),
			max_password_symbols: new IntegerField()
				.setDescription("Maximum password symbols")
				.setMinValue(6),

		}
	}

}