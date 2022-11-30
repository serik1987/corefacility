import {
	Routes,
	Route,
	Navigate
} from 'react-router-dom';

import CoreModule from 'corefacility-core/model/entity/CoreModule';

import BaseApp from 'corefacility-base/view/App';
import UserListWindow from './user-list/UserListWindow';
import UserDetailWindow from './user-list/UserDetailWindow';
import LogListWindow from './logs/LogListWindow';
import LogDetailWindow from './logs/LogDetailWindow';
import SettingsWindow from './settings/SettingsWindow';
import Window404 from './base/Window404';


/** This is the root component for the core application
 *  The component requires no props
 */
export default class App extends BaseApp{

	/** Class of the application model, if applicable
	 */
	static get applicationModelClass(){
		return CoreModule;
	}

	/** Renders all routes.
	 * 	@return {React.Component} the component must be <Routes> from 'react-dom-routes'.
	 */
	renderAllRoutes(){
		return (
			<Routes>
				<Route path="/logs/:lookup/" element={<LogDetailWindow/>} />
				<Route path="/logs/" element={<LogListWindow/>} />
				<Route path="/settings/" element={<SettingsWindow/>} />
				<Route path="/users/:lookup/" element={<UserDetailWindow/>} />
				<Route path="/users/" element={<UserListWindow/>} />
				<Route path="/" element={<Navigate to="/users/"/>} />
				<Route path="*" element={<Window404/>}/>
			</Routes>
		);
	}

}
