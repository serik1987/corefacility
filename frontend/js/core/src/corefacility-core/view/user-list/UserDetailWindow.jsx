import {useParams} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';

import NavigationWindow from '../base/NavigationWindow';
import Window404 from '../base/Window404';
import UserDetailForm from './UserDetailForm';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';


/** Provides viewing, modification and deletion of
 * 	single users
 */
class _UserDetailWindow extends NavigationWindow{

	constructor(props){
		super(props);
		this.handleNameChange = this.handleNameChange.bind(this);

		this.state = {
			userInformation: null,
		}
	}

	/** The browser title */
	get browserTitle(){
		return t("User information");
	}

	handleNameChange(newName){
		this._setBrowserTitle(newName);
		this.setState({
			userInformation: newName,
		});
	}

	render(){
		if (this.state.error404){
			return <Window404/>
		}

		return super.render();
	}

	/** Renders natvigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/users/">{t("User List")}</Hyperlink>,
			<p>{this.state.userInformation || t("User information")}</p>
		];
	}

	/** Renders all area below the very upper menu
	 * 	@return {React.Component} the rendered component
	 */
	renderContent(){
		return (<UserDetailForm 
			ref={this.setReloadCallback}
			inputData={{lookup: this.props.lookup}}
			on404={this.handle404}
			onNameChange={this.handleNameChange}
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