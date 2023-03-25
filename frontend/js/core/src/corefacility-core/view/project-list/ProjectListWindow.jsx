import {translate as t} from 'corefacility-base/utils';

import LivesearchWindow from 'corefacility-core/view/base/LivesearchWindow';

import ProjectListEditor from './ProjectListEditor';
import ProjectAddForm from './ProjectAddForm';


/** A base class for all window components that represent list of items and
 *  provide the livesearch on such list.
 * 	The window has no props
 * 
 *  Window state:
 * 		@param {string} searchTerm the search phrase entered by the user
 */
export default class ProjectListWindow extends LivesearchWindow{

	constructor(props){
		super(props);
		this.handleAddProject = this.handleAddProject.bind(this);
		this.registerModal('add-project', ProjectAddForm, {});
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Project List");
	}

	/** The search placeholder */
	get searchPrompt(){
		return t("Search on project name...")
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<ProjectListEditor
				searchTerm={this.state.searchTerm}
				onItemAddOpen={this.handleAddProject}
				ref={this.setReloadCallback}
			/>
		);
	}

	/**
	 *  Triggers when the user is trying to add some project
	 */
	async handleAddProject(event){
		return await this.openModal('add-project', {});
	}

}