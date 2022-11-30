import {ModelError} from './model';
import {translate as t} from '../utils';


export class NetworkError extends ModelError{

	constructor(e){
		super(t("Unable to connect to the server"));
		this.name = t("Connection error");
		console.error(e);
	}

}


export class HttpError extends ModelError{

	constructor(responseStatus, errorInfo){
		super(errorInfo.detail || t("The server returned error response without any details."));
		this.status = responseStatus;
		this.name = errorInfo.code || `${t("Error")} ${responseStatus}`;
		this.info = errorInfo;
		this.isDetailed = errorInfo.detail !== null && errorInfo.detail !== undefined;
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
