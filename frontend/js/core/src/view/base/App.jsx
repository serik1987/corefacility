import * as React from 'react';

import {NotImplementedError} from '../../exceptions/model.mjs';


/** Base class for application root components
 *  Requires no props
 */
export default class App extends React.Component{

	/** Set up the initial state. The Web server sent
	 *  the initial state during the index.html file rendering
	 *  and put this state inside the <script> elemen
	 */
	constructor(props){
		super(props);
		this.state = {
			token: window.SETTINGS.authorization_token,
			uuid: window.SETTINGS.app_uuid
		}

		window.application = this;
	}

	/** UUID for the current application */
	get uuid(){
		return this._uuid;
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

	/** Hides the general wait bar */
	componentDidMount(){
		let waitBar = document.getElementById("waitbar");
		if (waitBar !== null){
			waitBar.remove();
		}
	}

	render(){
		throw new NotImplementedError("render");
		return null;
	}

}