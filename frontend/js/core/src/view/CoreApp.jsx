import App from './base/App.jsx';
import UserListWindow from './user-list/UserListWindow.jsx';


/** This is the root component for the core application
 *  The component requires no props
 */
export default class CoreApp extends App{

	render(){
		return (<UserListWindow/>);
	}

}
