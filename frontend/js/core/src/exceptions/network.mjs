import {ModelError} from './model.mjs';


export class NetworkError extends ModelError{

	constructor(e){
		super("Unable to connect to the server");
		this.name = "Connection error";
		console.error(e);
	}

}


export class HttpError extends ModelError{

	constructor(responseStatus, errorInfo){
		super(errorInfo.detail || "The server returned error response without any details.");
		this.status = responseStatus;
		this.name = errorInfo.code || `Error ${responseStatus}`;
		this.info = errorInfo;
	}

}

export class BadRequestError extends HttpError{}

export class UnauthorizedError extends HttpError{}

export class ForbiddenError extends HttpError{}

export class NotFoundError extends HttpError{}

export class MethodNotAllowedError extends HttpError{}

export class NotAcceptableError extends HttpError{}

export class LengthRequiredError extends HttpError{}

export class TooManyRequestsError extends HttpError{}

export class ServerSideError extends HttpError{}
