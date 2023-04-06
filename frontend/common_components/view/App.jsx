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

const CHILD_FRAME_URL_TEMPLATE = /^\/ui\/[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}(.*)/;


/** Base class for application root components
 *  
 * 	Props (core application have no props, the other application contain information transmitted from the parent
 * 		application to the child one using the props):
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {object} 		translationResource 			translation resources for the i18next translation module.
 * 	@param {string}			token 							Authorization token received from the parent application.
 * 															undefined for the core application
 * 
 * 	State (core application sets its state during the authorization process. Another applications receive part of
 * 		their states from the parent's <ChildModuleFrame> component):
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 		token 							Authorization token received from the authorization
 * 															routines. null for any application except parent application
 * 	@param {string} 		reloadTime 						Timestamp of the last reload. This is required for the
 * 															interframe communication.
 */
export default class App extends DialogWrapper{

	/**
	 * 	Application name
	 */
	static getApplicationName(){
		throw new NotImplementedError('static getApplicationName');
	}

	/**
	 * 	Class of the application model, if applicable
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
			token: window.SETTINGS.authorization_token,
			reloadTime: new Date().valueOf()
		}

		window.application = this;
	}

	/**
	 * 	The application model.
	 */
	get model(){
		return this._module;
	}

	/** 
	 * 	Final authorization token that will be used by the HTTP client for the authorization processes.
	 */
	get token(){
		if (this.props.token){
			return this.props.token;
		} else {
			return this.state.token;
		}
	}

	/** Sets the authorization token. */
	set token(value){
		if (typeof value !== "string" && value !== null){
			throw new TypeError("The token must be string");
		}
		this.setState({token: value});
	}

	/** Currently authorized user */
	get user(){
		return this._user;
	}

	/** Sets the currently authorized user */
	set user(value){
		this._user = value;
	}

	/** true if the user was authorized, false otherwise */
	get isAuthorized(){
		return typeof this.token === "string";
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

	/**
	 * 	Receives entities from the parent applicatoin through the interframe communication (i.e., parent application
	 * 	runs this method to transmit its parent entities to this given application)
	 * 	@param {object} entityInfo 	It depends on the specification of the parent application. Explore this object for
	 * 	more details
	 */
	receiveParentEntities(entityInfo){
		throw new NotImplementedError('receiveParentEntities');
	}

	/**
	 * 	Reloads the data in child frames after the next application rendering
	 */
	reload(){
		this.setState({reloadTime: new Date().valueOf()});
	}

	notifyStateChanged(){
		console.log(this.constructor.getApplicationName());
		console.log(window.location.pathname);
		if (window.parent !== window){
			window.postMessage({
				method: 'pathChanged',
				info: window.location.pathname
			});
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
		let url = window.location.pathname;
		let matches = url.match(CHILD_FRAME_URL_TEMPLATE);
		if (matches !== null){
			window.history.replaceState(null, null, matches[1]);
		}

		if (window.SETTINGS.frontend_route && window.SETTINGS.frontend_route !== '/'){
			window.history.replaceState(null, null, window.SETTINGS.frontend_route);
			window.SETTINGS.frontend_route = undefined;
		}

		return (
			<Router>
				{ this.renderAllRoutes() }
				{ this.renderAllModals() }
			</Router>
		);
	}

	/**
	 * 	Renders the application.
	 * 	To create and load the application clear your src/index.js file and insert invocation of this
	 * 	method there.
	 */
	static renderApp(){
		if (typeof window.SETTINGS !== "object"){
			return <p style={{color: 'red'}}>The backend settings were not transmitted to frontend
				as window.SETTINGS object</p>;
		}
		let backendLang = window.SETTINGS.lang;
		let translationResource = null;
		let token = null;
		if (window.parent.application){
			translationResource = window.parent.application.props.translationResource;
			token = window.parent.application.token;
		}

		fetch(`/static/${this.getApplicationName()}/translation.${backendLang}.json`)
			.then(response => response.json())
			.then(result => {
				translationResource = {...translationResource, ...result};
				i18next
					.use(initReactI18next)
					.init({
						resources: {
							[backendLang]: {
								translation: translationResource,
							}
						},
						lng: backendLang,
						fallbackLng: 'en',
				});
			})
			.catch(error => {
				translationResource = {...translationResource};
				console.error(error);
				console.error("Failed to fetch language file. The language module will be switched off");
			})
			.finally(() => {
				let root = createRoot(document.getElementById("root"));
				let app = <this translationResource={translationResource} token={token}/>;
				root.render(app);
			});
	}

	componentDidMount(){
		let waitBar = document.getElementById("waitbar");
		if (waitBar !== null){
			waitBar.remove();
		}
		if (window !== window.parent){

			window.postMessage({
				method: 'applicationMount',
				info: null,
			}, window.location.origin);

			this.__dropDownCloser = window.addEventListener('click', event => {
				window.postMessage({
					method: 'click',
					info: null,
				}, window.location.origin);
			});
		}
	}

	componentWillUnmount(){
		window.removeEventListener(this.__dropDownCloser);
	}

}
