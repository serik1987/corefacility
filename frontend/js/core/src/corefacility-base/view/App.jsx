import {createRoot} from 'react-dom/client';
import {BrowserRouter as Router} from 'react-router-dom';
import i18next from 'i18next'
import {initReactI18next} from 'react-i18next';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import Module from 'corefacility-base/model/entity/Module';

import DialogWrapper from 'corefacility-base/view/DialogWrapper';
import MessageBox from 'corefacility-base/shared-view/components/MessageBox';
import QuestionBox from 'corefacility-base/shared-view/components/QuestionBox';
import PosixActionBox from 'corefacility-base/shared-view/components/PosixActionBox';


/** Base class for application root components
 *  Requires no props
 */
export default class App extends DialogWrapper{

	/** Class of the application model, if applicable
	 */
	static get applicationModelClass(){
		return Module;
	}

	/** Set up the initial state. The Web server sent
	 *  the initial state during the index.html file rendering
	 *  and put this state inside the <script> elemen
	 */
	constructor(props){
		super(props);
		this.registerModal("message", MessageBox);
		this.registerModal("question", QuestionBox);
		this.registerModal("posix_action", PosixActionBox);
		this._module = this.constructor.applicationModelClass.getIdentity();

		this.state = {
			token: window.SETTINGS.authorization_token
		}

		window.application = this;
	}

	/** Returns the application model */
	get model(){
		return this._module;
	}

	/** Authorization token.
	 *  You can't use API without the authorization token,
	 *  So, if this value is null, render the authorization component
	 */
	get token(){
		return this.state.token;
	}

	/** Sets the authorization token. */
	set token(value){
		if (typeof value !== "string" && value !== null){
			throw new TypeError("The token must be string");
		}
		this.setState({token: value});
	}

	/** true if the user was authorized, false otherwise */
	get isAuthorized(){
		return typeof this.state.token === "string";
	}

	/** Reloads the application model.
	 * 	Simply speaking, the function simply reloads all application settings	
	 * 	@async
	 * 	@return {Module} the reloaded model. Additionally, the reloaded module sets to the
	 * 	internal application fields.
	 */
	async reloadModel(){
		this._module = await this.constructor.applicationModelClass.get(this._module.uuid);
		return this._module;
	}

	/** Hides the general wait bar */
	componentDidMount(){
		let waitBar = document.getElementById("waitbar");
		if (waitBar !== null){
			waitBar.remove();
		}
	}

	/** Renders all routes.
	 * 	@abstract
	 * 	@return {React.Component} the component must be <Routes> from 'react-dom-routes'.
	 */
	renderAllRoutes(){
		throw new NotImplementedError("renderAllRoutes");
	}

	render(){
		return (
			<Router>
				{ this.renderAllRoutes() }
				{ this.renderAllModals() }
			</Router>
		);
	}

	static renderApp(ApplicationComponent){
		let app = <ApplicationComponent/>;
		if (typeof window.SETTINGS !== "object"){
			return <p style="color: red;">The backend settings were not transmitted to frontend
				as window.SETTINGS object</p>;
		}
		let backendLang = window.SETTINGS.lang;
		let root = createRoot(document.getElementById("root"));

		fetch(`/static/core/translation.${backendLang}.json`)
			.then(response => response.json())
			.then(result => {
				i18next
					.use(initReactI18next)
					.init({
						resources: {
							[backendLang]: {
								translation: result,
							}
						},
						lng: backendLang,
						fallbackLng: 'en',
				});
			})
			.catch(error => {
				console.error(error);
				console.error("Failed to fetch language file. The language module will be switched off");
			})
			.finally(() => {
				root.render(app);
			});
	}

}
