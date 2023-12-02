import {useParams} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import Sidebar from 'corefacility-base/shared-view/components/Sidebar';
import SidebarItem from 'corefacility-base/shared-view/components/SidebarItem';
import {ReactComponent as SettingsIcon} from 'corefacility-base/shared-view/icons/settings.svg';
import {ReactComponent as GroupIcon} from 'corefacility-base/shared-view/icons/group.svg';
import {ReactComponent as AdministrationIcon} from 'corefacility-base/shared-view/icons/administration.svg';
import {ReactComponent as AppRegistrationIcon} from 'corefacility-base/shared-view/icons/app_registration.svg';

import NavigationWindow from 'corefacility-core/view/base/NavigationWindow';
import Window404 from 'corefacility-core/view/base/Window404';

import ProjectSettingsForm from './ProjectSettingsForm';
import RootGroupLoader from './RootGroupLoader';
import ProjectPermissionEditor from './ProjectPermissionEditor';


/** 
 * 	A combined window that allows to set:
 * 		(a) project basic settings
 * 		(b) project's root group settings
 * 		(c) project basic settings
 * 	
 * 	Props:
 * 		@param {string} lookup 		alias of the project to deal with
 * 		@param {string} subroute 	one of the following values:
 * 			'settings' 		 window settings
 * 			'root'	   		 root group settings
 * 			'administration' administrator settings
 * 
 * 	State:
 * 	@param {boolean} error404 true will display the error404 window indicating
 * 	that such an entity was not found. false will do nothing
 * 	@param {string} projectName name of the project
 */
class _ProjectDetailWindow extends NavigationWindow{

	constructor(props){
		super(props);
		this.handleNoRootGroup = this.handleNoRootGroup.bind(this);

		this.state = {
			...this.state,
			noRootGroup: false,
		}
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return this.getWindowTitle(this.props.subroute)
	}

	/**
	 *  Returns the window title
	 * 	@param {string} subroute one of the subroutes
	 */
	getWindowTitle(subroute){
		switch (subroute){
		case 'settings':
			return t("Project settings");
		case 'root':
			return t("Project's root group");
		case 'administration':
			return t("Project administration");
		}
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/projects/">{t("Project List")}</Hyperlink>,
			<p>{this.state.projectName || this.getWindowTitle(this.props.subroute)}</p>,
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


		return (
			<Sidebar
				items={[
					<SidebarItem
						href={`/projects/${this.props.lookup}/`}
						current={this.props.subroute === 'settings'}
						icon={<SettingsIcon/>}
						text={t("Project settings")}
					/>,
					!this.state.noRootGroup && <SidebarItem
						href={`/projects/${this.props.lookup}/root/`}
						current={this.props.subroute === 'root'}
						icon={<GroupIcon/>}
						text={t("Project's root group")}
					/>,
					<SidebarItem
						href={`/projects/${this.props.lookup}/administration/`}
						current={this.props.subroute === 'administration'}
						icon={<AdministrationIcon/>}
						text={t("Project administration")}
					/>,
				]}
			>
				{this.props.subroute === 'settings' && <ProjectSettingsForm
					inputData={{lookup: this.props.lookup}}
					ref={this.setReloadCallback}
					on404={this.handle404}
					onNoRootGroup={this.handleNoRootGroup}
				/>}
				{this.props.subroute === 'root' && <RootGroupLoader
					projectAlias={this.props.lookup}
					ref={this.setReloadCallback}
					on404={this.handle404}
					onNoRootGroup={this.handleNoRootGroup}
				/>}
				{this.props.subroute === 'administration' && <ProjectPermissionEditor
					projectLookup={this.props.lookup}
					ref={this.setReloadCallback}
					on404={this.handle404}
					onNoRootGroup={this.handleNoRootGroup}
				/>}
			</Sidebar>
		);
	}

	render(){
		if (this.state.error404){
			return <Window404/>;
		}

		return super.render();
	}

	handleNoRootGroup(event){
		if (!this.state.noRootGroup){
			this.setState({noRootGroup: true});
		}
	}

}


/**
 *  Represents general project settings
 */
export function ProjectSettingsWindow(props){
	let {lookup} = useParams();
	return <_ProjectDetailWindow lookup={lookup} subroute="settings"/>;
}

/**
 *  Represents root group settings
 */
export function RootGroupSettingsWindow(props){
	let {lookup} = useParams();
	return <_ProjectDetailWindow lookup={lookup} subroute="root"/>;
}

/**
 * 	Represents project administration
 */
export function ProjectAdministrationWindow(props){
	let {lookup} = useParams();
	return <_ProjectDetailWindow lookup={lookup} subroute="administration"/>
}

