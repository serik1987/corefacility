class Application{

	constructor(){
		this._token = window.SETTINGS.authorization_token;
		this._uuid = window.SETTINGS.app_uuid;
	}

	get uuid(){
		return this._uuid;
	}

	get token(){
		return this._token;
	}

	get isAuthorized(){
		return !!this._token;
	}

}

window.application = new Application();