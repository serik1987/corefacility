import CONST from '../../const.mjs';
import '../../mock/window.mjs';
import {NotImplementedError, EntityStateError, ReadOnlyPropertyError} from '../../../src/exceptions/model.mjs';
import HttpRequestProvider from '../../../src/model/providers/http-request.mjs';
import client from '../../../src/model/providers/http-client.mjs';
import EntityPage from '../../../src/model/entity/page.mjs';


export default class BaseEntityTest{

	constructor(options = {}){
		this.entityClass = options.entityClass;
		this.defaultCreateArgs = options.defaultCreateArgs;
		this.entity = null;
	}

	checkDefaultArgs(entity){
		throw new NotImplementedError("checkDefaultArgs");
	}

	updateDefaultArgs(entity){
		throw new NotImplementedError("updateDefaultArgs");
	}

	checkUpdatedArgs(entity){
		throw new NotImplementedError("checkUpdatedArgs");
	}

	checkEntityLocked(entity){
		expect(() => this.updateDefaultArgs(entity)).toThrow(EntityStateError);
		expect(() => entity.create()).rejects.toThrow(EntityStateError);
		expect(() => entity.update()).rejects.toThrow(EntityStateError);
		expect(() => entity.delete()).rejects.toThrow(EntityStateError);
	}

	defineValueTestData(){
		throw new NotImplementedError("defineValueTestData");
	}

	isResponsePaginated(){
		throw new NotImplementedError('isResponsePaginated');
	}

	defineFilterTestData(){
		throw new NotImplementedError("defineFilterTestData");
	}

	defineLookupField(){
		return "alias";
	}

	async ensureEntityNotExists(){
		throw new NotImplementedError("ensureEntityNotExists");
	}

	async createEntity(){
		this.entity = new this.entityClass(this.defaultCreateArgs);
		await this.entity.create();
	}

	async reloadEntity(){
		await this.createEntity();
		this.entity = await this.entityClass.get(this.entity.id);
	}

	async findEntity(){
		throw new NotImplementedError("findEntity");
	}

	async beforeAll(){}

	async beforeEach(){}

	auxTests(){}

	async afterEach(){}

	async afterAll(){}

	describe(){

		let self = this;
		let valueTestData = this.defineValueTestData();

		beforeAll(async () => {
			await window.authorize(CONST.origin, CONST.api_version);
			await self.ensureEntityNotExists();
			await self.beforeAll();
		});

		beforeEach(async () => {
			await self.beforeEach();
		});

		afterEach(async () => {
			await self.afterEach();
			if (self.entity !== null && self.entity.state !== "deleted"){
				await self.entity.delete();
			}
			self.entity = null;
		});

		afterAll(async () => {
			await self.afterAll();
		});

		/* Transition state diagram method */

		test("transition CREATING state", () => {
			let entity = new self.entityClass(self.defaultCreateArgs);
			expect(entity.id).toBeNull();
			expect(entity.state).toBe("creating");
			self.checkDefaultArgs(entity);
			self.updateDefaultArgs(entity);
			expect(entity.id).toBeNull();
			expect(entity.state).toBe("creating");
			expect(() => entity.update()).rejects.toThrow(EntityStateError);
			expect(() => entity.delete()).rejects.toThrow(EntityStateError);
		});
		
		test("transition CREATING -> PENDING state", () => {
			let entity = new self.entityClass(self.defaultCreateArgs);
			let promise = entity.create()
				.then(() => {
					self.entity = entity;
				});
			expect(entity.id).toBeNull();
			expect(entity.state).toBe("pending");
			self.checkDefaultArgs(entity);
			self.checkEntityLocked(entity);
			return promise;
		});

		test("transition CREATING -> PENDING -> SAVED state", async () => {
			await self.createEntity();
			expect(self.entity.id).toBeTruthy();
			expect(self.entity.state).toBe("saved");
			self.checkDefaultArgs(self.entity);
			expect(() => self.entity.create()).rejects.toThrow(EntityStateError);
			let t0 = new Date();
			await self.entity.update();
			let t1 = new Date();
			let actualUpdateTime = t1 - t0;
			expect(actualUpdateTime).toBeLessThan(10);
		});

		test("transition CREATING -> PENDING -> SAVED -> CHANGED state", async() => {
			await self.createEntity();
			self.updateDefaultArgs(self.entity);
			expect(self.entity.id).toBeTruthy();
			expect(self.entity.state).toBe("changed");
			self.updateDefaultArgs(self.entity);
			expect(() => self.entity.create()).rejects.toThrow(EntityStateError);
		});

		test("transition CREATING -> PENDING -> SAVED -> CHANGED -> PENDING state", () => {
			return self.createEntity().then(() => {
				let id = self.entity.id;
				self.updateDefaultArgs(self.entity);
				let promise = self.entity.update();
				expect(self.entity.id).toEqual(id);
				expect(self.entity.state).toEqual('pending');
				self.checkUpdatedArgs(self.entity);
				self.checkEntityLocked(self.entity);
				return promise;
			});
		});

		test("transition CREATING -> PENDING -> SAVED -> CHANGED -> PENDING -> SAVED", async () => {
			await self.createEntity();
			let oldId = self.entity.id;
			self.updateDefaultArgs(self.entity);
			await self.entity.update();
			expect(self.entity.id).toBe(oldId);
			expect(self.entity.state).toBe("saved");
			self.checkUpdatedArgs(self.entity);
		});

		test("transition LOADED (get by ID)", async() => {
			await self.createEntity();
			let oldId = self.entity.id;
			let entity = await self.entityClass.get(self.entity.id);
			expect(entity.id).toBe(oldId);
			expect(entity.state).toBe("loaded");
			self.checkDefaultArgs(entity);
			expect(() => entity.create()).rejects.toThrow(EntityStateError);
			let t0 = new Date();
			await entity.update();
			let t1 = new Date();
			expect(t1 - t0).toBeLessThan(10);
		});

		test("transition LOADED -> CHANGED", async() => {
			await self.reloadEntity();
			let oldId = self.entity.id;
			self.updateDefaultArgs(self.entity);
			expect(self.entity.id).toBe(oldId);
			expect(self.entity.state).toBe("changed");
			self.checkUpdatedArgs(self.entity);
		});

		test("transition CREATING -> PENDING -> SAVED -> PENDING", () => {
			return self.createEntity()
				.then(() => {
					let oldId = self.entity.id;
					let promise = self.entity.delete();
					expect(self.entity.id).toBe(oldId);
					expect(self.entity.state).toBe("pending");
					self.checkDefaultArgs(self.entity);
					self.checkEntityLocked(self.entity);
					return promise;
				});
		});

		test("transition CREATING -> PENDING -> SAVED -> PENDING -> DELETED", async () => {
			await self.createEntity();
			await self.entity.delete();
			expect(self.entity.id).toBeNull();
			expect(self.entity.state).toBe("deleted");
			self.checkEntityLocked(self.entity);
		});

		test("transition CREATING -> PENDING -> SAVED -> CHANGED -> PENDING (towards DELETED)", () => {
			return self.createEntity()
				.then(() => {
					self.updateDefaultArgs(self.entity);
					let oldId = self.entity.id;
					let promise = self.entity.delete();
					expect(self.entity.id).toBe(oldId);
					expect(self.entity.state).toBe("pending");
					self.checkEntityLocked(self.entity);
					return promise;
				});
		});

		test("transition CREATING -> PENDING -> SAVED -> CHANGED -> PENDING -> DELETED", async () => {
			await self.createEntity();
			self.updateDefaultArgs(self.entity);
			await self.entity.delete();
			expect(self.entity.id).toBeNull();
			expect(self.entity.state).toBe("deleted");
			self.checkEntityLocked(self.entity);
		});

		test("transition LOADED -> PENDING", () => {
			return self.reloadEntity()
				.then(() => {
					let oldId = self.entity.id;
					let promise = self.entity.delete();
					expect(self.entity.id).toBe(oldId);
					expect(self.entity.state).toBe("pending");
					self.checkEntityLocked(self.entity);
					return promise;
				});
		});

		test("transition LOADED -> PENDING -> DELETED", async () => {
			await self.reloadEntity();
			await self.entity.delete();
			expect(self.entity.id).toBeNull();
			expect(self.entity.state).toBe("deleted");
			self.checkEntityLocked(self.entity);
		});

		test("transition FOUND", async() => {
			await self.findEntity();
			expect(self.entity.id).toBeTruthy();
			expect(self.entity.state).toBe("found");
			self.checkDefaultArgs(self.entity);
			expect(() => self.updateDefaultArgs(self.entity)).toThrow(EntityStateError);
			expect(() => self.entity.create()).rejects.toThrow(EntityStateError);
			expect(() => self.entity.update()).rejects.toThrow(EntityStateError);
		});

		test("transition FOUND -> PENDING", async() => {
			return self.findEntity()
				.then(() => {
					let oldId = self.entity.id;
					let promise = self.entity.delete();
					expect(self.entity.id).toBe(oldId);
					expect(self.entity.state).toBe("pending");
					self.checkEntityLocked(self.entity);
					return promise;
				});
		});

		test("transition FOUND -> PENDING -> DELETED", async() => {
			await self.findEntity();
			await self.entity.delete();
			expect(self.entity.id).toBeNull();
			expect(self.entity.state).toBe("deleted");
			self.checkEntityLocked(self.entity);
		});

		for (let fieldName in valueTestData){

			if (valueTestData[fieldName].read_only){
				test(`negative field test ${fieldName}`, async () => {
					await self.createEntity();
					expect(() => { self.entity[fieldName] = "some-value"; }).toThrow(ReadOnlyPropertyError);
				});
			} else {
				if (valueTestData[fieldName].valid_value !== undefined){
					test(`positive field test ${fieldName}`, async () => {
						await self.createEntity();
						self.entity[fieldName] = valueTestData[fieldName].valid_value;
						await self.entity.update();
						let entity = await self.entityClass.get(self.entity.id);
						expect(entity[fieldName]).toEqual(valueTestData[fieldName].recovered_value);
					});
				}

				if (valueTestData[fieldName].invalid_value !== undefined){
					test(`negative field test ${fieldName}`, async () => {
						await self.createEntity();
						self.entity[fieldName] = valueTestData[fieldName].invalid_value;
						try{
							await self.entity.update();
							throw new Error("The entity update promise shall never be resolved in this case!");
						} catch (e){
							expect(e).toHaveProperty(`info.${fieldName}`);
						}
					});
				}
			}

		}

		test("checking for enough fields", async () => {
			let mainProvider = null;
			for (let provider of self.entityClass._entityProviders){
				if (provider instanceof HttpRequestProvider){
					mainProvider = provider;
					break;
				}
			}
			let entityListUrl = mainProvider._getEntityListUrl();
			let responseData = await client.request(entityListUrl, "OPTIONS", null);
			let fieldData = responseData.actions.POST;
			for (let fieldName in fieldData){
				expect(valueTestData).toHaveProperty(fieldName);
				expect(valueTestData).toHaveProperty(`${fieldName}.read_only`, fieldData[fieldName].read_only);
				expect(self.entityClass.isFieldRequired(fieldName)).toBe(fieldData[fieldName].required);
			}
		});

		if (self.isResponsePaginated()){

			test.each(self.defineFilterTestData())("testing filter: %s",
				async (queryParams, expectedEntitySet, pageLength) => {
				let pageIndex = 0;
				let page = null;
				let totalEntityList = [];
				let lookupField = self.defineLookupField();
				if (queryParams !== null){
					page = await self.entityClass.find(queryParams);
				} else {
					page = await self.entityClass.find();
				}
				do {
					expect(page.pageCount).toBe(pageLength[pageIndex]);
					for (let entity of page){
						totalEntityList.push(entity);
					}
					if (!page.isLastPage){
						pageIndex++;
						await page.next();
					}
				} while (!page.isLastPage);
				expect(totalEntityList.filter(entity => !expectedEntitySet.has(entity[lookupField]))).toHaveLength(0);
			});

		}

		self.auxTests();
	}
}