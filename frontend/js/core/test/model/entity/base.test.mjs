import '../../mock/window.mjs';
import Entity from '../../../src/model/entity/base.mjs';
import {NotImplementedError} from '../../../src/exceptions/model.mjs';


describe("base tests for the Entity class", () => {

	test("abstract methods", () => {
		expect(() => Entity._entityName).toThrow(NotImplementedError);
		expect(() => Entity._defineEntityProviders()).toThrow(NotImplementedError);
		expect(() => Entity._definePropertyDescription()).toThrow(NotImplementedError);
	});

});