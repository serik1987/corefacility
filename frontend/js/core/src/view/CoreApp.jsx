import {
	Routes,
	Route,
	Navigate
} from 'react-router-dom';

import App from './base/App.jsx';
import UserListWindow from './user-list/UserListWindow.jsx';
import UserDetailWindow from './user-list/UserDetailWindow.jsx';
import LogListWindow from './logs/LogListWindow.jsx';
import Window404 from './base/Window404.jsx';


/** This is the root component for the core application
 *  The component requires no props
 */
export default class CoreApp extends App{

	/** Renders all routes.
	 * 	@return {React.Component} the component must be <Routes> from 'react-dom-routes'.
	 */
	renderAllRoutes(){
		return (
			<Routes>
				<Route path="/logs/" element={<LogListWindow/>} />
				<Route path="/users/:lookup/" element={<UserDetailWindow/>} />
				<Route path="/users/" element={<UserListWindow/>} />
				<Route path="/" element={<Navigate to="/users/"/>} />
				<Route path="*" element={<Window404/>}/>
			</Routes>
		);
	}

}
