import {wait} from '../src/utils.mjs';

describe("utils wait function", () => {

	test("utils wait function: positive test", async () => {
		let expectedFulfillmentTime = 1000;
		let maxBias = 500;

		let t0 = new Date();
		await wait(expectedFulfillmentTime);
		let t1 = new Date();
		let actualFulfillmentTime = t1 - t0;
		let eps = Math.abs(actualFulfillmentTime - expectedFulfillmentTime);
		expect(eps).toBeLessThan(maxBias);
	});

	test("utils wait function: negative test", async () => {
		let waitTime = -1000;

		await expect(wait(waitTime)).rejects.toBeInstanceOf(RangeError);
	});

});
