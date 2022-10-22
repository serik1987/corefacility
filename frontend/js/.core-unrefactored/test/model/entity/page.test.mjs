import CONST from '../../const.mjs';
import '../../mock/window.mjs';
import User from '../../../src/model/entity/user.mjs';



describe("entity page test", () => {

	let page = null;

	beforeAll(async() => {
		await window.authorize(CONST.origin, CONST.api_version);
		page = await User.find({profile: "light"});
	});

	test("transition state diagram", async () => {
		let firstPageUsers = [];
		for (let user of firstPageUsers){
			firstPageUsers.push(user.id);
		}
		expect(page.isFirstPage).toBe(true);
		expect(page.isLastPage).toBe(false);
		expect(() => page.previous()).rejects.toThrow(RangeError);
		await page.next();
		expect(page.isFirstPage).toBe(false);
		expect(page.isLastPage).toBe(true);
		expect(() => page.next()).rejects.toThrow(RangeError);
		await page.previous();
		let lastPageUsers = [];
		for (let user of lastPageUsers){
			lastPageUsers.push(user.id);
		}
		expect(lastPageUsers).toEqual(firstPageUsers);
	});

});