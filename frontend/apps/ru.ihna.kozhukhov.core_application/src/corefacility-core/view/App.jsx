import {
	Routes,
	Route,
	Navigate
} from 'react-router-dom';

import CoreModule from 'corefacility-core/model/entity/CoreModule';
import Profile from 'corefacility-base/model/entity/Profile';

import BaseApp from 'corefacility-base/view/App';
import UserListWindow from './user-list/UserListWindow';
import UserDetailWindow from './user-list/UserDetailWindow';
import LogListWindow from './logs/LogListWindow';
import LogDetailWindow from './logs/LogDetailWindow';
import SettingsWindow from './settings/SettingsWindow';
import Window404 from './base/Window404';
import AuthorizationForm from './AuthorizationForm';
import ProfileWindow from './profile/ProfileWindow';
import GroupListWindow from './group-list/GroupListWindow';
import GroupUserWindow from './group-list/GroupUserWindow';
import ProjectListWindow from './project-list/ProjectListWindow';
import {ProjectSettingsWindow, RootGroupSettingsWindow, ProjectAdministrationWindow} 
	from './project-list/project-detail-windows';
import ProjectApplicationListWindow from './application-list/ProjectApplicationListWindow';
import SystemInformationWindow from './system-information/SystemInformationWindow';
import ProcessListWindow from './system-information/ProcessListWindow';
import OsLogWindow from './system-information/OsLogWindow';


/** This is the root component for the core application
 *  The component requires no props
 */
export default class App extends BaseApp{

	constructor(props){
		super(props);

		if (window.SETTINGS.auth_user !== null){
			this._user = Profile.deserialize(window.SETTINGS.auth_user);
		} else {
			this._user = null;
		}
	}

	/**
	 * 	Returns the application name
	 */
	static getApplicationName(){
		return 'ru.ihna.kozhukhov.core_application';
	}

	/** Class of the application model, if applicable
	 */
	static get applicationModelClass(){
		return CoreModule;
	}

	/** Activation code in case activation link was detected, null otherwise */
	get activationCode(){
		return new URLSearchParams(window.location.search).get('activation_code');
	}

	/** Renders all routes.
	 * 	@return {React.Component} the component must be <Routes> from 'react-dom-routes'.
	 */
	renderAllRoutes(){
		if (window.parent !== window.top){
			return <p style={{color: 'red'}}>The 'core' application can't be launched in the iframe</p>;
		}
		else if (this.token !== null && this.activationCode === null){
			let adminPermissions = window.application.user.is_superuser;
			let noSupportPermission = !window.application.user.is_support;
			let defaultUrl = "/projects/";

			return (
				<Routes>
					<Route path="/projects/:lookup/apps/" element={<ProjectApplicationListWindow/>}/>
					<Route path="/projects/:lookup/administration/" element={<ProjectAdministrationWindow/>}/>
					<Route path="/projects/:lookup/root/" element={<RootGroupSettingsWindow/>}/>
					<Route path="/projects/:lookup/" element={<ProjectSettingsWindow/>}/>
					<Route path="/projects/" element={<ProjectListWindow/>}/>
					<Route path="/groups/:lookup/" element={<GroupUserWindow/>}/>
					<Route path="/groups/" element={<GroupListWindow/>}/>
					{adminPermissions && <Route path="/logs/:lookup/" element={<LogDetailWindow/>} />}
					{adminPermissions && <Route path="/logs/" element={<LogListWindow/>} />}
					{noSupportPermission && <Route path="/profile/" element={<ProfileWindow/>}/>}
					{adminPermissions && <Route path="/settings/" element={<SettingsWindow/>} />}
					{adminPermissions && <Route path="/users/:lookup/" element={<UserDetailWindow/>} />}
					{adminPermissions && <Route path="/users/" element={<UserListWindow/>} />}
					<Route path="/sysinfo/" element={<SystemInformationWindow/>}/>
					<Route path="/procinfo/" element={<ProcessListWindow/>}/>
					<Route path="/os-logs/" element={<OsLogWindow/>}/>
					<Route path="/" element={<Navigate to={defaultUrl}/>} />
					<Route path="*" element={<Window404/>}/>
				</Routes>
			);
		} else {
			return <AuthorizationForm/>;
		}
	}

}
