import '../application.mjs';
import {
	HttpError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
	MethodNotAllowedError, NotAcceptableError, LengthRequiredError, TooManyRequestsError,
	ServerSideError, NetworkError
}
from '../../exceptions/network.mjs';
import {wait} from '../../utils.mjs';


const HTTP_ERROR_CODES = {
	400: BadRequestError,
	401: UnauthorizedError,
	403: ForbiddenError,
	404: NotFoundError,
	405: MethodNotAllowedError,
	406: NotAcceptableError,
	411: LengthRequiredError,
	429: TooManyRequestsError,
}


const SERVER_SIDE_ERROR_MIN = 500;
const DJANGO_THROTTLE_ERROR_CODE = 429;
const MAX_5xx_POOL_SIZE = 3;
const POOL_WAIT = 1000;


class HttpClient{

	constructor(){
		this._requestNumber = 0;
	}

	get requestNumber(){
		return this._requestNumber;
	}

	get(url){
		return this.request(url, "GET", null);
	}

	post(url, data){
		return this.request(url, "POST", data);
	}

	put(url, data){
		return this.request(url, "PUT", data);
	}

	patch(url, data){
		return this.request(url, "PATCH", data);
	}

	delete(url){
		return this.request(url, "DELETE", null, false);
	}

	request(url, method, data, isJsonResponse = true){
		this._requestNumber++;
		document.dispatchEvent(new CustomEvent("request", {detail: this._requestNumber}));
		let headers = new Headers();
		headers.set("Content-Type", "application/json");
		headers.set("Accept", "application/json");
		if (window.application.isAuthorized){
			headers.set("Authorization", `Token ${window.application.token}`);
		}
		let requestOptions = {
			method: method,
			headers: headers
		};
		if (data !== null){
			requestOptions.body = JSON.stringify(data);
		}
		let self = this;
		return (function poolingFunction(poolNumber = 0){
			return fetch(url, requestOptions)
				.catch(e => {
					throw new NetworkError(e);
				})
				.then(response => {
					if (!response.ok){
						return self.processErrorResponse(response, poolingFunction, poolNumber)
					}
					else if (isJsonResponse){
						return response.json();
					}
					else {
						return null;
					}
				})
		})()
			.finally(() => {
				--self._requestNumber;
				document.dispatchEvent(new CustomEvent("response", {detail: self._requestNumber}));
			});;
	}

	processErrorResponse(response, poolingFunction, poolNumber){	
		if (response.status === DJANGO_THROTTLE_ERROR_CODE){
			let retryAfter = parseInt(response.headers.get("Retry-After")) * 1000;
			return wait(retryAfter).then(() => poolingFunction());
		}
		else {
			return response.json()
				.catch(e => {
					return {
						'detail': response.status >= SERVER_SIDE_ERROR_MIN ? "Internal server error" : "The response body is not presented in JSON format",
					}
				})
				.then(errorData => {
					if (response.status >= SERVER_SIDE_ERROR_MIN){
						poolNumber += 1;
						if (poolNumber <= MAX_5xx_POOL_SIZE){
							return wait(POOL_WAIT)
								.then(() => poolingFunction());
						} else {
							throw new ServerSideError(response.status, errorData);
						}
					}
					else if (response.status in HTTP_ERROR_CODES){
						throw new HTTP_ERROR_CODES[response.status](response.status, errorData);
					}
					else {
						throw new HttpError(response.status, errorData);
					}
				});
		}
	}

}

let client = new HttpClient();

export default client;