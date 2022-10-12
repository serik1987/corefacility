import {jest} from '@jest/globals';
import fetch, {Headers} from "node-fetch";

import CustomEvent from './custom-event.mjs';
import Document from './document.mjs';

export default class WindowMock{

	constructor(){
		globalThis.CustomEvent = CustomEvent;
		globalThis.Document = Document;
		if (!globalThis.fetch){
			globalThis.fetch = jest.fn(fetch);
			globalThis.Headers = Headers;
		}
	}

	authorize(origin, clientVersion, uuid=null){
		this.origin = origin;
		this.clientVersion = clientVersion;
		this.token;
		this.uuid = uuid;
		return fetch(`${this.origin}/api/${this.clientVersion}/login/`, {method: "POST"})
			.then(response => {
				expect(response.status).toBe(200);
				return response.json();
			})
			.then(responseData => {
				this.token = responseData.token;
			});
	}

	get SETTINGS(){
		return {
			frontend_route: '/',
			iframe_route: '/',
			app_uuid: this.uuid,
			authorization_token: this.token,
			client_version: this.clientVersion
		}
	}

}


if (!globalThis.window){
	globalThis.window = new WindowMock();
}
