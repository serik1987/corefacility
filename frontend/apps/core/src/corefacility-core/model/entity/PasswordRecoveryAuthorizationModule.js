import Module from 'corefacility-base/model/entity/Module';
import DurationField from 'corefacility-base/model/fields/DurationField';


/** Provides serialization, deserialization and validation of settings
 * 	for the password recovery module
 */
export default class PasswordRecoveryAuthorizationModule extends Module{

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @abstract
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			password_recovery_lifetime: new DurationField()
				.setDescription("Password recovery lifetime"),
		}
	}

}