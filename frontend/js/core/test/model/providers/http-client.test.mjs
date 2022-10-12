import {jest} from '@jest/globals';

import CONST from '../../const.mjs';
import WindowMock from '../../mock/window.mjs';
import client from '../../../src/model/providers/http-client.mjs';
import {
	HttpError,
	NetworkError,
	UnauthorizedError,
	NotFoundError,
	MethodNotAllowedError,
	BadRequestError,
	ForbiddenError,
	ServerSideError,
}
from '../../../src/exceptions/network.mjs';



describe("HTTP client test", () => {

	const USER_DATA = {
		login: "serik1987",
		name: "Sergei",
		surname: "Kozhukhov",
		email: "sergei.kozhukhov@ihna.ru",
	}

	const POOL_NUMBER = 3;
	const TOTAL_POOL_WAIT = 2000;

	let userListUrl = null;
	let userId = null;

	function checkRequestState(requestNumber, eventNumber, lastEventType, lastEventDetail){
		expect(client.requestNumber).toBe(requestNumber);
		expect(document.dispatchEvent.mock.calls.length).toBe(eventNumber);
		if (eventNumber > 0){
			expect(document.dispatchEvent.mock.lastCall[0]).toEqual({
				eventType: lastEventType,
				eventOptions: {
					detail: lastEventDetail
				}
			});
		}
	}

	beforeAll(async () => {
		await window.authorize(CONST.origin, CONST.api_version);
		userListUrl = `${window.origin}/api/${window.clientVersion}/users/`;
	});

	afterEach(async () => {
		if (userId){
			await client.delete(`${userListUrl}${userId}/`);
			userId = null;
		}
		document.dispatchEvent.mockClear();
		globalThis.fetch.mockClear();
	});

	test("GET request - positive test", () => {
		checkRequestState(0, 0);
		let promise = client.get(userListUrl)
			.then(responseData => {
				expect(responseData).toHaveProperty("count");
				expect(responseData).toHaveProperty("previous");
				expect(responseData).toHaveProperty("next");
				checkRequestState(0, 2, "response", 0);
				
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("GET request - network error", () => {
		checkRequestState(0, 0);
		let promise = client.get("some fake url")
			.then(responseData => {
				fail("The promise shall never be resolved!");
			})
			.catch (e => {
				checkRequestState(0, 2, 'response', 0);
				expect(e).toBeInstanceOf(NetworkError);
			});
		checkRequestState(1, 1, 'request', 1);
		return promise;
	});

	test("GET request - authorization error", () => {
		let token = window.application.token;
		window.application.token += "pss";
		checkRequestState(0, 0);
		let promise = client.get(userListUrl)
			.then(responseData => {
				fail("The promise shall never be resolved");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(UnauthorizedError);
				checkRequestState(0, 2, "response", 0);
			});
		window.application.token = token;
		checkRequestState(1, 1, "request", 1);
		return promise;
	});


	test("GET request - not found", () => {
		checkRequestState(0, 0);
		let promise = client.get(userListUrl + "fake-user")
			.then(responseData => {
				fail("The promise shall never be resolved");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(NotFoundError);
				checkRequestState(0, 2, "response", 0);
			})
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("GET request - method not allowed", () => {
		checkRequestState(0, 0);
		let promise = client.get(`${window.origin}/api/${window.clientVersion}/login/`)
			.then(responseData => {
				fail("The promise shall never be resolved!");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(MethodNotAllowedError);
				checkRequestState(0, 2, 'response', 0);
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("GET request - not JSON", () => {
		checkRequestState(0, 0);
		let promise = client.get(`${window.origin}`)
			.then(responseData => {
				fail("The promise shall never be resolved!");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(SyntaxError);
				checkRequestState(0, 2, "response", 0);
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	for (let n = 2; n <= 7; ++n){

		test(`GET request - ${n} simultaneous requests`, () => {
			let promiseList = [];
			checkRequestState(0, 0);

			let responseCounter = 0;
			for (let k = 0; k < n; ++k){
				let promise = client.get(userListUrl)
					.then(responseData => {
						expect(responseData).toHaveProperty("results");
						responseCounter++;
						checkRequestState(n - responseCounter, n + responseCounter, "response", n - responseCounter);
					});
				promiseList.push(promise);
				checkRequestState(k+1, k+1, "request", k+1);
			}

			return Promise.all(promiseList);
		});

	}

	test("GET request - forbidden", async() => {
		checkRequestState(0, 0);
		let promise = client.get(`${window.origin}/api/${window.clientVersion}/profile/`)
			.then(responseData => {
				console.log(responseData);
				fail("The promise shall never be resolved!");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(ForbiddenError);
				checkRequestState(0, 2, "response", 0);
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("POST request - positive test", () => {
		checkRequestState(0, 0);
		let promise = client.post(userListUrl, USER_DATA)
			.then(responseData => {
				expect(responseData).toHaveProperty("id");
				userId = responseData.id;
				checkRequestState(0, 2, "response", 0);
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("POST request - bad request", () => {
		checkRequestState(0, 0);
		let promise = client.post(userListUrl, {})
			.then(responseData => {
				fail("The promise shall never be resolved!");
			})
			.catch(e => {
				expect(e).toBeInstanceOf(BadRequestError);
				expect(e).toHaveProperty("info.login");
				checkRequestState(0, 2, "response", 0);
			});
		checkRequestState(1, 1, "request", 1);
		return promise;
	});

	test("PUT request - positive test", async () => {
		let userData = await client.post(userListUrl, USER_DATA);
		userId = userData.id;
		userData.email = "serik1987@gmail.com";
		delete userData.phone;
		checkRequestState(0, 2, "response", 0);
		let promise = client.put(`${userListUrl}${userData.id}/`, userData)
			.then(responseData => {
				expect(responseData.id).toBe(userData.id);
				checkRequestState(0, 4, "response", 0);
			});
		checkRequestState(1, 3, "request", 1);
		return promise;
	});

	test("PATCH request - positive test", async () => {
		let userData = await client.post(userListUrl, USER_DATA);
		userId = userData.id;
		checkRequestState(0, 2, "response", 0);
		let promise = client.patch(`${userListUrl}${userId}/`, {email: "serik1987@gmail.com"})
			.then(responseData => {
				expect(responseData).toHaveProperty("email", "serik1987@gmail.com");
				checkRequestState(0, 4, "response", 0);
			});
		checkRequestState(1, 3, "request", 1);
		return promise;
	});

	test("DELETE request - positive test", async () => {
		let userData = await client.post(userListUrl, USER_DATA);
		userId = userData.id;
		checkRequestState(0, 2, "response", 0);
	});

	test("request pooling", async () => {
		globalThis.fetch.mockImplementation((url, options) => {
			return Promise.resolve({
				ok: false,
				status: 500,
				json: () => Promise.reject(new ReferenceError("This is not a JSON content")),
			});
		});
		let t0 = new Date();
		checkRequestState(0, 0);
		try{
			await client.get(userListUrl);
			fail("The client.get() promise can't be fulfilled under permanent error 500")
		}
		catch (e) {
			expect(e).toBeInstanceOf(ServerSideError);
			expect(globalThis.fetch.mock.calls.length).toBe(POOL_NUMBER);
			let t1 = new Date();
			let waitTime = t1 - t0;
			let waitTimeBias = Math.abs(TOTAL_POOL_WAIT - waitTime);
			expect(waitTimeBias).toBeLessThan(500);
			checkRequestState(0, 2, "response", 0);
		}
		finally{
			globalThis.fetch.mockReset();
		}
	});

	test("test 402 response", async () => {
		globalThis.fetch.mockImplementationOnce((url, options) => {
			return Promise.resolve({
				ok: false,
				status: 402,
				json: () => Promise.reject(new ReferenceError("This is not a JSON content")),
			});
		});
		try{
			await client.get(userListUrl);
			fail("The client.get() can't be fulfilled when response 402 Payment Required received");
		}
		catch (e){
			expect(e).toBeInstanceOf(HttpError);
		}
	});

});