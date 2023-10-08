import {translate as t} from 'corefacility-base/utils';

import LivesearchWindow from 'corefacility-core/view/base/LivesearchWindow';

import GroupListEditor from './GroupListEditor';
import GroupAddBox from './GroupAddBox';


/**
 * This window represents list of all groups
 * 
 *  A base class for all window components that represent list of items and
 *  provide the livesearch on such list.
 * 	The window has no props
 * 
 *  Window state:
 * 		@param {string} searchTerm the search phrase entered by the user
 */
export default class GroupListWindow extends LivesearchWindow{

	constructor(props){
		super(props);

		this.addNewGroup = this.addNewGroup.bind(this);

		this.registerModal('add_group', GroupAddBox, {});
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Group list");
	}

	/** The search placeholder */
	get searchPrompt(){
		return t("Search by group name...");
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
			<GroupListEditor
				onItemAddOpen={this.addNewGroup}
				ref={this.setReloadCallback}
				searchTerm={this.state.searchTerm}
			/>
		);
	}

	/**
	 * Prepares new group for the add
	 */
	async addNewGroup(){
		return await this.openModal('add_group', {});
	}

}