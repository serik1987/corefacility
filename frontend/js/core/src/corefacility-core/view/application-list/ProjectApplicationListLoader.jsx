import {translate as t} from 'corefacility-base/utils';
import InstalledApplicationListLoader from 'corefacility-base/view/InstalledApplicationListLoader';

import Project from 'corefacility-core/model/entity/Project';
import CoreWindowHeader from 'corefacility-core/view/base/CoreWindowHeader';

import InstalledProjectApplicationList from './InstalledProjectApplicationList';


/**
 * 	Represents list of all installed applications attached directly to a given project (i.e., to 'projects' entry point)
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 		projectLookup 		ID or alias of the project which application list is required to be
 * 												displayed.
 * 	@param {callback} 		on404 				Triggers when no requested resource was found. Callback has no
 * 												arguments.
 * 	@param {callback} 		onProjectFound		Triggers when the project has been found. Callback arguments:
 * 		@param {string} name 						Name of the project that has been found
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	_isLoading, _isError, _error props are nor specified for direct access. Use instead:
 * 		(a) isLoading, isError, error Javascript properties
 * 		(b) reportListFetching, reportFetchSuccess(itemList), reportFetchFailure(error) methods
 * 	@param {string} 		editorHeader 		Header for the editor
 * 
 * 	Props for the descendant items:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback} 		onItemSelect 		Triggers when the user selects a given item
 * 
 */
export default class ProjectApplicationListLoader extends InstalledApplicationListLoader{

	constructor(props){
		super(props);

		this._project = null;

		this.state = {
			...this.state,
			editorHeader: t("Project application list"),
		}
	}

	/**
	 *  Returns a URI for the application list fetching (see documentation for details)
	 */
	get applicationFetchUri(){
		return `/api/${window.SETTINGS.client_version}/core/projects/${this.props.projectLookup}/`;
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return InstalledProjectApplicationList;
	}

	/**
	 * 	Processes additional information attached to the application list
	 * 	@param {object}		fetchResult			The information returned by the server.
	 */
	processAttachInformation(fetchResult){
		if (!fetchResult.project_info){
			throw new Error("To backend developers: project_info must be within the response result!");
		}
		this._project = Project.deserialize(fetchResult.project_info);
		this.setState({editorHeader: this._project.name});
		if (this.props.onProjectFound){
			this.props.onProjectFound(this._project.name);
		}
	}

	render(){
		return (
			<CoreWindowHeader
				isLoading={this.isLoading}
				isError={this.isError}
				error={this.error}
				header={t("Project application list") + ": " + this.state.editorHeader}
			>
				{this.renderItemList()}
			</CoreWindowHeader>
		);
	}

	/** Renders the item list.
	 *  This function must be invoked from the render() function.
	 */
	renderItemList(){
		let ItemList = this.entityListComponent;
		return (<ItemList
			items={this.itemList}
			isLoading={this.isLoading}
			isError={this.isError}
			ref={this.registerItemList}
			project={this._project}
		/>);
	}

}