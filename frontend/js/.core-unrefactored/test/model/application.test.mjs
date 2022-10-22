import OPTIONS from '../const.mjs';
import WindowMock from '../mock/window.mjs';
import '../../src/model/application.mjs';

describe("Application test", () => {

	beforeAll(async () => {
		await globalThis.window.authorize(OPTIONS.origin, OPTIONS.api_version);
	});

	test("public properties", () => {
		let application = globalThis.window.application;
		expect(application.uuid).toBeNull();
		expect(application.token).toEqual(globalThis.window.token);
		expect(application.isAuthorized).toBe(true);
		expect(() => { application.token = 42; }).toThrow(TypeError);
	});

});
