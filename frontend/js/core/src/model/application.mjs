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

	set token(value){
		if (typeof value !== "string" && value !== null){
			throw new TypeError("The token must be string");
		}
		this._token = value;
	}

	get isAuthorized(){
		return !!this._token;
	}

}

let application = null;

Object.defineProperty(window, "application", {
	get(){
		if (application === null){
			application = new Application();
		}
		return application;
	}
});
