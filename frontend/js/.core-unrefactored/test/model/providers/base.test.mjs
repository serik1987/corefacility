import '../../mock/window.mjs';
import {NotImplementedError} from '../../../src/exceptions/model.mjs';
import EntityProvider from '../../../src/model/providers/base.mjs';
import User from '../../../src/model/entity/user.mjs';

describe("Base entity provider tests", () => {

	test("Tests for non-valid search parameters", async () => {
		expect(() => User.find(42)).rejects.toThrow(TypeError);
	});

	test("Tests abstract interface functions", async () => {
		let provider = new EntityProvider(User);
		let user = new User({});
		expect(() => provider.createEntity()).toThrow(NotImplementedError);
		expect(() => provider.updateEntity()).toThrow(NotImplementedError);
		expect(() => provider.deleteEntity()).toThrow(NotImplementedError);
		expect(() => provider.deleteEntity()).toThrow(NotImplementedError);
		expect(() => provider.loadEntity()).toThrow(NotImplementedError);
		expect(() => provider.findEntities()).toThrow(NotImplementedError);
		expect(provider.toString().match(/EntityProvider/)).not.toBeNull();
	});

});