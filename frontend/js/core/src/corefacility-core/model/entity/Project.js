import Entity from 'corefacility-base/model/entity/Entity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {StringField, ReadOnlyField} from 'corefacility-base/model/fields';
import FileField from 'corefacility-base/model/fields/FileField';
import RelatedField from 'corefacility-base/model/fields/RelatedField';
import {SlugValidator} from 'corefacility-base/model/validators';
import RootGroupField from 'corefacility-core/model/fields/RootGroupField';

import Group from './Group';
import User from './User';


/**
 * 	Represents a single project
 */
export default class Project extends Entity{

	/** Returns the human-readable entity name
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Project";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [new HttpRequestProvider('projects', Project)];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			alias: new StringField()
				.setDescription("Project alias")
				.setRequired(true)
				.addValidator(SlugValidator)
					.parent,
			avatar: new FileField(project => `projects/${project.id}/avatar/`)
				.setDescription("URL for the project icon static file"),
			name: new StringField()
				.setDescription("Project name")
				.setRequired(true),
			root_group: new RootGroupField()
				.setDescription("Governing group")
				.setRequired(true),
			description: new StringField()
				.setDescription("Project description"),
			governor: new RelatedField(User, false)
				.setDescription("Project leader"),
			project_dir: new ReadOnlyField()
				.setDescription("The project home directory"),
			unix_group: new ReadOnlyField()
				.setDescription("UNIX group")
		}
	}

}