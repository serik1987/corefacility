import {
	BrowserRouter as Router,
	Routes,
	Route,
	Navigate
} from 'react-router-dom';

import App from './base/App.jsx';
import UserListWindow from './user-list/UserListWindow.jsx';
import UserDetailWindow from './user-list/UserDetailWindow.jsx';
import Window404 from './base/Window404.jsx';


/** This is the root component for the core application
 *  The component requires no props
 */
export default class CoreApp extends App{

	render(){
		return (
			<Router>
				<Routes>
					<Route path="/users/:lookup/" element={<UserDetailWindow/>} />
					<Route path="/users/" element={<UserListWindow/>} />
					<Route path="/" element={<Navigate to="/users/"/>} />
					<Route path="*" element={<Window404/>}/>
				</Routes>
			</Router>
		);
	}

}
