import BaseEntityTest from './base.mjs';
import User from '../../../src/model/entity/user.mjs';
import {EntityPropertyError} from '../../../src/exceptions/model.mjs';
import {NotFoundError, NetworkError} from '../../../src/exceptions/network.mjs';


export default class UserTest extends BaseEntityTest{

	constructor(options = {
		entityClass: User,
		defaultCreateArgs: {login: "serik1987"}
	}){
		super(options);
	}

	checkDefaultArgs(user){
		expect(user.login).toBe("serik1987");
	}

	updateDefaultArgs(user){
		user.login = "sergei_kozhukhov";
		expect(user.login).toBe("sergei_kozhukhov");
	}

	checkUpdatedArgs(user){
		expect(user.login).toBe("sergei_kozhukhov");
	}

	defineValueTestData(){
		return {
			id: {
				read_only: true,
			},
			login: {
				read_only: false,
				valid_value: "sergei_kozhukhov",
				recovered_value: "sergei_kozhukhov",
				invalid_value: "",
			},
			name: {
				read_only: false,
				valid_value: "Sergei",
				recovered_value: "Sergei",
				invalid_value: undefined,
			},
			surname: {
				read_only: false,
				valid_value: "Kozhukhov",
				recovered_value: "Kozhukhov",
				invalid_value: undefined,
			},
			avatar: {
				read_only: true,
			},
			is_password_set: {
				read_only: true,
			},
			email: {
				read_only: false,
				valid_value: "sergei.kozhukhov@ihna.ru",
				recovered_value: "sergei.kozhukhov@ihna.ru",
				invalid_value: "sergei",
			},
			phone: {
				read_only: false,
				valid_value: "+7 000 000 00 00",
				recovered_value: "+7 000 000 00 00",
				invalid_value: "some wrong phone number",
			},
			is_locked: {
				read_only: false,
				valid_value: true,
				recovered_value: true,
				invalid_value: undefined,
			},
			is_superuser: {
				read_only: false,
				valid_value: true,
				recovered_value: true,
				invalid_value: undefined,
			},
			is_support: {
				read_only: true,
			},
			unix_group: {
				read_only: true,
			},
			home_dir: {
				read_only: true,
			}
		}
	}

	isResponsePaginated(){
		return true;
	}

	simulateNetworkProblem(){
		fetch.mockImplementationOnce(() => {
			return Promise.reject(new TypeError("Sudden network problems..."));
		});
	}
	
	defineFilterTestData(){
		let fullLoginSet = new Set(['support', 'user1', 'user2', 'user3', 'user4',
			'user5', 'user6', 'user7', 'user8', 'user9', 'user10']);
		let userLoginSet = new Set(fullLoginSet);
		let iljaSet = new Set(['user4', "user8"]);
		let tsvetkovSet = new Set(['user5']);
		let emptySet = new Set();
		userLoginSet.delete('support');
		return [
			{
				queryParams: {profile: "light", q: "Цветков"},
				expectedEntitySet: tsvetkovSet,
				pageLength: [1],
			},
			{
				queryParams: {profile: "light", q: "khhfkgkjhf"},
				expectedEntitySet: emptySet,
				pageLength: [0],
			},
			{
				queryParams: {profile: "basic", q: "Цветков"},
				expectedEntitySet: tsvetkovSet,
				pageLength: [1],
			},
			{
				queryParams: {q: "user"},
				expectedEntitySet: userLoginSet,
				pageLength: [10],
			},
			{
				queryParams: {profile: "light"},
				expectedEntitySet: fullLoginSet,
				pageLength: [6, 5],
			},
			{
				queryParams: {profile: "light", q: "user"},
				expectedEntitySet: userLoginSet,
				pageLength: [6, 4],
			},
			{
				queryParams: null,
				expectedEntitySet: fullLoginSet,
				pageLength: [11],
			},
			{
				queryParams: {profile: "basic", q: "Илья"},
				expectedEntitySet: iljaSet,
				pageLength: [2],
			},
			{
				queryParams: {profile: "basic", q: "kdfjhgkdhfjgkj"},
				expectedEntitySet: emptySet,
				pageLength: [0],
			},
			{
				queryParams: {profile: "light", q: "Илья"},
				expectedEntitySet: iljaSet,
				pageLength: [2],
			},
			{
				queryParams: {q: "Цветков"},
				expectedEntitySet: tsvetkovSet,
				pageLength: [1],
			},
			{
				queryParams: {q: "Илья"},
				expectedEntitySet: iljaSet,
				pageLength: [2],
			},
			{
				queryParams: {q: "user"},
				expectedEntitySet: userLoginSet,
				pageLength: [10],
			},
			{
				queryParams: {profile: "basic"},
				expectedEntitySet: fullLoginSet,
				pageLength: [11],
			}
		].map(params => [params.queryParams, params.expectedEntitySet, params.pageLength]);

	}

	defineLookupField(){
		return "login";
	}

	async findEntity(){
		await this.createEntity();
		let entityList = (await User.find({"q": "serik1987"}));
		for (let entity of entityList){
			this.entity = entity;
			break;
		}
	}

	async ensureEntityNotExists(){
		for (let login of ['serik1987', 'sergei_kozhukhov']){
			try{
				let user = await User.get(login);
				await user.delete();
			} catch (e){
				if (!(e instanceof NotFoundError)){
					throw e;
				}
			}
		}
	}

	auxTests() {

		let self = this;

		test("user create - on failure", async () => {
			let user = new User({login: "serik1987"});
			self.simulateNetworkProblem();
			try{
				await user.create();
				throw new Error("Can't be reached here!");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(user.state).toBe("creating");
				self.checkDefaultArgs(user);
			}
		});

		test("user update - on failure", async () => {
			await self.createEntity();
			self.entity.login = "sergei_kozhukhov";
			let oldId = self.entity.id;
			self.simulateNetworkProblem();
			try{
				await self.entity.update();
				throw new Error("can't be reached here!");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(self.entity.id).toBe(oldId);
				expect(self.entity.state).toBe("changed");
				self.checkUpdatedArgs(self.entity);
			}
		});

		test("user delete (from saved state) - on failure", async () => {
			await self.createEntity();
			self.simulateNetworkProblem();
			try{
				await self.entity.delete();
				throw new Error("can't be reached here!");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(self.entity.id).toBeTruthy();
				expect(self.entity.state).toBe("saved");
				self.checkDefaultArgs(self.entity);
			}
		});

		test("user delete (from changed state) - on failure", async () => {
			await self.createEntity();
			self.entity.login = "sergei_kozhukhov";
			self.simulateNetworkProblem();
			try{
				await self.entity.delete();
				throw new Error("can't be reached here");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(self.entity.id).toBeTruthy();
				expect(self.entity.state).toBe("changed");
				self.checkUpdatedArgs(self.entity);
			}
		});

		test("user delete (from loaded state) - on failure", async () => {
			await self.reloadEntity();
			self.simulateNetworkProblem();
			try{
				await self.entity.delete();
				throw new Error("can't be reached here!");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(self.entity.id).toBeTruthy();
				expect(self.entity.state).toBe("loaded");
				self.checkDefaultArgs(self.entity);
			}
		});

		test("user delete (from found) - on failure", async () => {
			await self.createEntity();
			let userPage = await User.find({q: "serik1987"});
			let user = null;
			for (let currentUser of userPage){
				user = currentUser;
				break;
			}
			self.simulateNetworkProblem();
			try{
				await user.delete();
				throw new Error("can't reached this!");
			} catch (e){
				expect(e).toBeInstanceOf(NetworkError);
				expect(user.id).toBe(self.entity.id);
				expect(user.state).toBe("found");
				self.checkDefaultArgs(self.entity);
			}
		});

		test("user reload", async() => {
			await self.createEntity();
			let user = await self.entity.reload();
			expect(user.id).toBe(self.entity.id);
			expect(user.state).toBe("loaded");
			self.checkDefaultArgs(user);
		});

		test("to string", async () => {
			let user = new User({});
			user.toString();
		});

		test("setting fake field", async () => {
			expect(() => new User({"fake property": "fake value"})).toThrow(EntityPropertyError);
		});

	}

}