import Module from 'corefacility-base/model/entity/Module';
import {IntegerField} from 'corefacility-base/model/fields';


/** Describes the 'Standard authorization' module */
export default class StandardAuthorizationModule extends Module{

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			max_failed_authorization_number: new IntegerField()
				.setMinValue(5)
				.setDescription("Maximum number of failed authorizations")
				.setRequired(true)
		}
	}

}