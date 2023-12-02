import {useParams} from 'react-router-dom';
import styled from 'styled-components';

import {translate as t} from 'corefacility-base/utils';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import NavigationWindow from 'corefacility-core/view/base/NavigationWindow';
import Window404 from 'corefacility-core/view/base/Window404';


/** 
 * 	This component is deprecated and will be replaced in the nearest future.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 	projectLookup	Alias or ID of the project which application list must be displayed.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	@param {string} 	projectName 	Name of the project to be found
 */
class _ProjectApplicationListWindow extends NavigationWindow{

	constructor(props){
		super(props);
		this.handleProjectFound = this.handleProjectFound.bind(this);

		this.state = {
			...this.state,
			projectName: null,
		}
	}

	/**
	 *  Default title of the browser tab.
	 */
	get browserTitle(){
		return t("Project application list");
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/projects/">{t("Project List")}</Hyperlink>,
			<p>{this.state.projectName ?? this.browserTitle}</p>
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
		const Message = styled.p`
			padding-left: 30px;
			padding-right: 26px;
			font-style: italic;
		`;

		return (
			<Message>{t("This area is under construction. Please, accept our appologizes for the temporary inconvenience.")}</Message>
		);
	}

	render(){
		if (this.state.error404){
			return <Window404/>
		}

		return super.render();
	}

	/**
	 * 	Triggers when child component has found the project
	 */
	handleProjectFound(name){
		this.setState({projectName: name});
		this._setBrowserTitle(name);
	}

}


/** Represents list of all applications connected to the 'projects' entry point that are (a) applications; (b) enabled;
 * 	(c) connected to the project; (d) connection is enabled.
 * 
 * 	The component deals with URL parameter lookup
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	no props
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	@param {string} 	projectName 	Name of the project to be found
 */
export default function ProjectApplicationListWindow(props){
	let {lookup} = useParams();

	return <_ProjectApplicationListWindow projectLookup={lookup}/>;
}