import {
	HttpError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
	MethodNotAllowedError, NotAcceptableError, LengthRequiredError, TooManyRequestsError,
	ServerSideError, NetworkError
}
from '../../exceptions/network.mjs';
import {wait, translate as t} from '../../utils.mjs';


/** The object contains information about all HTTP errors
 *  Each property name is HTTP status code and each value is an exception
 *  that must be thrown in response to that code
 */
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

/** The minimum of all error codes indicating that there are server-side troubles */
const SERVER_SIDE_ERROR_MIN = 500;

/** The error code that indicates that max. number of requests exceeded */
const DJANGO_THROTTLE_ERROR_CODE = 429;

/** If the response status indicate about server problem, the HttpClient repeat the
 *  same request given number of times and then throws an error
 */
const MAX_5xx_POOL_SIZE = 3;

/** If the response status indicate about server-side problem and number of request
 *  repetitions doesn't exceed the MAX_5xx_POOL_SIZE, the HttlClient will wait for
 *  a given amount of ms and then repat the request
 */
const POOL_WAIT = 1000;


/** This is the basic class that provides interaction between this application and
 *  the Web server.
 *  The class is an improved version of the Javascript's fetch() function. The class
 *  can do everything as fetch() function does. Besides it, it can:
 *      (1) Retry the request after given number of seconds when error 429 (Too Many Requests)
 * 			received
 * 		(2) Retry the request three times when there are server side problems
 * 		(3) Automatically choose the format of the input and output data
 * 		(4) Convert promise fullfillments to rejections when 4xx and 5xx responses received
 * 	    (5) Put authorization token to the request headers, if the authorization token has
 * 			already been received from the Web Server.
 */
class HttpClient{

	FILE_UPLOAD_METHOD = "PATCH";

	/**
	 *  Creates new HTTP client
	 *  The HTTP client creates only once ans is accessible from the client variable
	 */
	constructor(){
		this._requestNumber = 0;
	}

	/** Number of simultaneous request that serve at a time of the object call */
	get requestNumber(){
		return this._requestNumber;
	}

	/** Sends GET request to the server. The request body is assumed to be in JSON format
	 *  @async
	 *  @param {string|URL} url that request url
	 *  @return {object} the response body already parsed
	 */
	get(url){
		return this.request(url, "GET", null);
	}

	/** Sends POST request to the server. The request and response bodies were both
	 *  assumed to be in JSON format
	 * 	@async
	 *  @param {string|URL} url the requested url
	 *  @param {object} data - the request body that will be stringified
	 *  @return {object} the response body that has already been parsed
	 */
	post(url, data){
		return this.request(url, "POST", data);
	}

	/** Sends the PUT request to the server. The request and response bodies were both
	 *  assumed to be in JSON format
	 *  @async
	 *  @param {string|URL} url the requested url
	 *  @param {object} data the request body that will be stringified
	 *  @return {object} the response body that has already been parsed
	 */
	put(url, data){
		return this.request(url, "PUT", data);
	}

	/** Sends the PATCH request to the server. The request and response bodies were both
	 *  assumed to be in JSON format
	 *  @async
	 *  @param {string|URL} url the requested url
	 *  @param {object} data the request body that will be stringified
	 *  @return {object} the response body that has already been parsed
	 */
	patch(url, data){
		return this.request(url, "PATCH", data);
	}

	/** Sends the DELETE request to the server. The request and response bodies were both
	 *  assumed to be in JSON format
	 *  @async
	 *  @param {string|URL} url the requested url
	 *  @return {undefined}
	 */
	delete(url){
		return this.request(url, "DELETE", null, false);
	}

	/** Senda an arbitrary request to the Web server. The request is assumed to accept
	 *  JSON data or empty body and respond with either JSON data or empty body
	 *  @async
	 * 	@param {string|URL} url the requested URL
	 *  @param {string} method the request method written in the upper case
	 *  @param {object|null} data the request body that will be stringified. Use null
	 * 						 if the request contains no body
	 *  @param {boolean} isJsonResponse true if the response body is assumed to be in JSON
	 * 	   				 format, false if the response body is assumed to be empty
	 * 	@return {object} Response body on success. When isJsonResponse = false, null will be returned
	 */
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
			});
	}

	/** Uploads single file to the server
	 * 	@async
	 *  @param {string|URL} the requested URL
	 * 	@param {File} the file to be uploaded
	 * 	@return {object} the response body on success
	 */
	upload(url, file){
		let self = this;
		this._requestNumber++;
		document.dispatchEvent(new CustomEvent("request", {detail: this._requestNumber}));

		let headers = new Headers();
		headers.set("Accept", "application/json");
		if (window.application.isAuthorized){
			headers.set("Authorization", `Token ${window.application.token}`);
		}

		let formData = new FormData();
		formData.set("file", file);
		let requestOptions = {
			method: this.FILE_UPLOAD_METHOD,
			headers: headers,
			body: formData,
		}

		return (function poolingFunction(poolNumber = 0){
			return fetch(url, requestOptions)
				.catch(e => {
					throw new NetworkError(e);
				})
				.then(response => {
					if (!response.ok){
						return self.processErrorResponse(response, poolingFunction, poolNumber);
					} else {
						return response.json();
					}
				})
		})()
			.finally(() => {
				self._requestNumber--;
				document.dispatchEvent(new CustomEvent("response", {detail: self._requestNumber}));
			});
	}

	/** Parses error (i.e., 4xx or 5xx) responses
	 *  @async
	 *  @param {Response} the HTTP response that is assumed to have bad status
	 *  @param {poolingFunction} the function that will be invoked in the following cases:
	 * 		- when status code is 429 (Too Many Requests) the client reads the Retry-After response header
	 * 			waits for a given number of seconds and invoke poolingFunction() again
	 *      - when status code if 500 or greater (Server Side Errors) the client waits for a second
	 * 			and invoke the poolingFunction again if it has been called insufficient number of times
	 * @param {number} poolNumber number of times that the poolingFunctions was invoked after server-side
	 * 		           errors.
	 */
	processErrorResponse(response, poolingFunction, poolNumber){	
		if (response.status === DJANGO_THROTTLE_ERROR_CODE){
			let retryAfter = parseInt(response.headers.get("Retry-After")) * 1000;
			return wait(retryAfter).then(() => poolingFunction());
		}
		else {
			return response.json()
				.catch(e => {
					return {
						'detail': response.status >= SERVER_SIDE_ERROR_MIN ? t("Internal server error") : t("The response body is not presented in JSON format"),
					}
				})
				.then(errorData => {
					if (response.status >= SERVER_SIDE_ERROR_MIN){
						poolNumber += 1;
						if (poolNumber < MAX_5xx_POOL_SIZE){
							return wait(POOL_WAIT)
								.then(() => poolingFunction(poolNumber));
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

/** The only instance of the HttpClient class that must be invoked */
let client = new HttpClient();

export default client;