import {useParams} from 'react-router-dom';

import {translate as t} from '../../utils.mjs';
import CoreWindow from '../base/CoreWindow.jsx';
import Window404 from '../base/Window404.jsx';
import UserDetailForm from './UserDetailForm.jsx';


/** Provides viewing, modification and deletion of
 * 	single users
 */
class _UserDetailWindow extends CoreWindow{

	/** The browser title */
	get browserTitle(){
		return t("User information");
	}

	render(){
		if (this.state.error404){
			return <Window404/>
		}

		return super.render();
	}

	/**	Renders the area between corefacility logo and icons on the top right
	 * 	@return {React.Component} the rendered component
	 */
	renderControls(){
		return null;
	}

	/** Renders all area below the very upper menu
	 * 	@return {React.Component} the rendered component
	 */
	renderContent(){
		return (<UserDetailForm 
			ref={this.setReloadCallback}
			inputData={{lookup: this.props.lookup}}
			on404={this.handle404}
		/>)
	}

}


/** Provides viewing, modification and deletion of
 * 	single users
 */
export default function UserDetailWindow(props){

	/* Sorry, class-based component are not able to extract router parameters */
	let {lookup} = useParams();

	return <_UserDetailWindow lookup={lookup} {...props} />
}