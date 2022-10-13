import CONST from '../../const.mjs';
import '../../mock/window.mjs';
import client from '../../../src/model/providers/http-client.mjs';
import User from '../../../src/model/entity/user.mjs';


describe("HTTP request tests", () => {

	beforeAll(async () => {
		await window.authorize(CONST.origin, CONST.api_version);
	});

	test("find all user - print as single page", async () => {
		let oldUsers = await User.find();
		let userListUrl = `${window.origin}/api/${window.clientVersion}/users/`;
		let responseData = await client.get(userListUrl);
		fetch.mockImplementationOnce(() => {
			return Promise.resolve({
				ok: true,
				status: 200,
				json: () => { return Promise.resolve(responseData.results); }
			});
		});
		let users = await User.find();
		expect(users.length).toBe(oldUsers.totalCount);
		let userIndex = 0;
		for (let user of oldUsers){
			expect(users[userIndex].id).toBe(user.id);
			userIndex++;
		}
	});

	test("toString()", () => {
		let provider = User._entityProviders[User.SEARCH_PROVIDER_INDEX];
		expect(provider.toString().match(/UsersProvider/)).not.toBeNull();
	});

});