import Module from 'corefacility-base/model/entity/Module';
import {BooleanField, IntegerField, StringField} from 'corefacility-base/model/fields';
import {ChoiceValidator, UrlValidator} from 'corefacility-base/model/validators';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';


/** Describes the 'Synchronization with IHNA Website' pseudo-module.
 */
export default class IhnaSynchronizationModule extends Module{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Ihna Synchronization pseudo-module";
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {object} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			auto_add: new BooleanField()
				.setRequired()
				.setDescription("Automatically add new employees"),
			auto_update: new BooleanField()
				.setRequired()
				.setDescription("Automatically update new employees"),
			auto_remove: new BooleanField()
				.setRequired()
				.setDescription("Automatically delete new employees"),
			ihna_website: new StringField()
				.setRequired()
				.addValidator(UrlValidator)
					.parent
				.setDescription("The website address"),
			language: new StringField()
				.setRequired()
				.addValidator(ChoiceValidator)
					.setChoices(["ru", "en"])
					.parent
				.setDescription("Employees list language"),
			page_length: new IntegerField()
				.setRequired()
				.setMinValue(1)
				.setDescription("Number of users that will be fetched during a single request"),
		};
	}

}