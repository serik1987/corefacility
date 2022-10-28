import {translate as t} from '../../utils.mjs';
import LivesearchWindow from '../base/LivesearchWindow.jsx';
import UserListEditor from './UserListEditor.jsx';
import UserAddBox from './UserAddBox.jsx';


/** Window that shows list of all users
 * 
 *  Window state:
 * 		@param {string} searchTerm the search phrase entered by the user
 */
export default class UserListWindow extends LivesearchWindow{

	constructor(props){
		super(props);
		this.registerModal("add-user", UserAddBox);
	}

	/** The web browser title */
	get browserTitle(){
		return t("User List");
	}

	/** Returns the search prompt for the user list window */
	get searchPrompt(){
		return t("Search by first name, last name, login...");
	}

	/** Renders the user list editor
	 *  @return {React.js component}
	 */
	 renderContent(){
	 	return (<UserListEditor
	 		q={this.state.searchTerm}
	 		ref={this.setReloadCallback}
	 		onUserAddOpen={() => this.openModal("add-user")}
	 	/>);
	 }

}
