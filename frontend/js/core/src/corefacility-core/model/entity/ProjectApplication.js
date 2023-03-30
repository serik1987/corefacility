import ChildEntity from 'corefacility-base/model/entity/ChildEntity';
import HttpRequestProvider from 'corefacility-base/model/providers/HttpRequestProvider';
import {StringField, ReadOnlyField, BooleanField} from 'corefacility-base/model/fields';


/**
 *  Manages project applications, attaches application to the project, detaches application from the project
 */
export default class ProjectApplication extends ChildEntity{

	/** Returns the human-readable entity name
	 *  @abstract
	 *  @static
	 *  @return {string} the entity name
	 */
	static get _entityName(){
		return "Project Application";
	}

	/** Initializes the list of all entity providers. The function invokes once during the initiation of
	 *  the very first entity object. During the entity development, the functions allows to attach given
	 *  entity provider to the entity
	 *  @return [list{EntityProvider}] list of all entity providers
	 */
	static _defineEntityProviders(){
		return [new HttpRequestProvider('projects/:id:/apps', ProjectApplication, true)];
	}

	/** Initializes property descriptions.
	 *  The method invokes only once. When you create new entity class you must redefine this method
	 *  and describe all entity fields by the {field_name: instance_of_EntityField} pair
	 *  @return {objecty} an object that will be used for field value retrievals and set
	 */
	static _definePropertyDescription(){
		return {
			uuid: new StringField()
				.setDescription("Application UUID"),
			name: new ReadOnlyField()
				.setDescription("Application name"),
			permissions: new ReadOnlyField()
				.setDescription("Application permissions"),
			is_enabled: new BooleanField()
				.setDescription("The link is enabled"),
		}
	}

	/**
	 * 	Creates new link between the project and the application.
	 * 	@param {Project} project 			The project to add
	 * 	@param {Application} application 	The application to add
	 * 	@return {ProjectApplication} 		New ProjectApplication object
	 */
	static new(project, application){
		let projectApplication = new ProjectApplication({is_enabled: true, uuid: application.uuid}, project);
		return projectApplication;
	}

	/**
	 * 	The model object unique identifier
	 */
	get id(){
		return this.uuid;
	}

}