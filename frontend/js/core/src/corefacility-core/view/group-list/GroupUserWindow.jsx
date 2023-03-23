import {useParams} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import Group from 'corefacility-core/model/entity/Group';
import NavigationWindow from 'corefacility-core/view/base/NavigationWindow';
import Window404 from 'corefacility-core/view/base/Window404';

import GroupUserEditor from './GroupUserEditor';


/** 
 * 	A window with navigation bar (so called 'breadcrumbs')
 * 
 * 	Props:
 * 	@param {Number} groupId ID of the group which users shall be displayed
 * 
 * 	State:
 * 	@param {boolean} error404 true will display the error404 window indicating
 * 	that such an entity was not found. false will do nothing
 * 	@param {string} groupName name of the group
 */
class _GroupUserWindow extends NavigationWindow{

	constructor(props){
		super(props);
		this.handleGroupFound = this.handleGroupFound.bind(this);

		this.state = {
			...this.state,
			name: null,
		}
	}

	/**
	 * Name of the group or some short info, if the group name is not accessible
	 */
	get name(){
		return (this.state && this.state.name) || t("Group users list");
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return this.name;
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/groups/">{t("Group list")}</Hyperlink>,
			<p>{this.name}</p>,
		];
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (<GroupUserEditor
			groupId={this.props.groupId}
			name={this.name}
			ref={this.setReloadCallback}
			on404={this.handle404}
			onGroupFound={this.handleGroupFound}
		/>);
	}

	render(){
		if (this.state.error404){
			return <Window404/>;
		}

		return super.render();
	}

	/**
	 * Triggers when the only child component has found the group
	 * @param {Group} group 	group that has been found
	 */
	handleGroupFound(group){
		this.setState({name: group.name});
		this._setBrowserTitle(group.name);
	}

}


/**
 * 	This is a wrapper to the group users window (see _GroupUsersWindow) that
 * 	transforms router parameter to prop.
 * 	@param {object} props useless
 */
export default function GroupUserWindow(props) {
	let {lookup} = useParams();
	let groupId = parseInt(lookup);
	if (isNaN(groupId)){
		return <Window404/>;
	} else {
		return <_GroupUserWindow {...props} groupId={groupId}/>;
	}
}
