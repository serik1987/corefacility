import ChildEntity from 'corefacility-base/model/entity/ChildEntity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {StringField, IntegerField, FloatField} from 'corefacility-base/model/fields';
import FileField from 'corefacility-base/model/fields/FileField';
import {SlugValidator} from 'corefacility-base/model/validators';


/**
 * 	Represents a single functional map.
 */
export default class FunctionalMap extends ChildEntity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Functional Map";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 * 	@static
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [
			new HttpRequestProvider('core/projects/:id:/imaging/data', FunctionalMap),
		];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @abstract
	 * 	@static
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			alias: new StringField()
				.setDescription("Map alias")
				.setRequired()
				.addValidator(SlugValidator)
					.parent,
			data: new FileField(entity => `projects/${entity.parent.id}/imaging/data/${entity.id}/npy/`)
				.setDescription("Map file"),
			type: new StringField()
				.setDescription("Map alias"),
			resolution_x: new IntegerField()
				.setDescription("Map resolution, x")
				.setMinValue(10),
			resolution_y: new IntegerField()
				.setDescription("Map resolution, y")
				.setMinValue(10),
			width: new FloatField()
				.setDescription("Map width, um")
				.setMinValue(0.0),
			height: new FloatField()
				.setDescription("Map height, um")
				.setMinValue(0.0),
		}
	}


}