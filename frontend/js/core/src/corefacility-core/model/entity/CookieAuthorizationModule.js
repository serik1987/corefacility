import Module from 'corefacility-base/model/entity/Module';
import DurationField from 'corefacility-base/model/fields/DurationField';


/** Represents module for the cookie authorization
 */
export default class CookieAuthorizationModule extends Module{

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			'cookie_lifetime': new DurationField()
				.setDescription("Cookie lifetime")
		}
	}

}