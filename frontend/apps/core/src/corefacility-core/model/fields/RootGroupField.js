import RelatedField from 'corefacility-base/model/fields/RelatedField';
import EntityState from 'corefacility-base/model/entity/EntityState';
import Group from 'corefacility-core/model/entity/Group';


/**
 *  This entity provides read and write access to the project's root_group field
 */
export default class RootGroupField extends RelatedField{

	constructor(){
		super(Group, false);
	}

	/**
	 *  Injects the value to the root group field
	 * 	@param {Project} entitty 		a project to which the value must be injected
	 * 	@param {string} propertyName	expected to be root_group
	 * 	@param {Group} value 			a value to assign
	 * 	@return {undefined}
	 */
	proofread(entity, propertyName, value){
		if (value === null){
			entity._entityFields.root_group_id = undefined;
			entity._entityFields.root_group_name = undefined;
			return undefined;
		}

		if (!(value instanceof Group)){
			throw new Error("The field's value must be an instance of Group");
		}
		if (propertyName !== 'root_group'){
			throw new Error("The field type RootGroupField is suitable only for 'root_group'");
		}

		if (value.state === EntityState.creating){
			entity._entityFields.root_group_id = null;
			entity._entityFields.root_group_name = value.name;

			entity._propertiesChanged.add('root_group_id');
			entity._propertiesChanged.add('root_group_name');

			return undefined;

		} else {
			entity._entityFields.root_group_id = value.id;
			entity._propertiesChanged.add('root_group_id');
			return undefined;
		}
	}

}