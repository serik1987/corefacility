import '../../mock/window.mjs';
import EntityField from '../../../src/model/fields/field.mjs';
import User from '../../../src/model/entity/user.mjs';


describe("Auxiliary entity field tests", () => {

	test("Test field read/write properties", () => {
		let field = new EntityField("mail@nobody.ru", "string", "E-mail", false);
		expect(field.default).toBe("mail@nobody.ru");
		expect(field.description).toBe("E-mail");
	});

	test("Trying to assign incorrect field", () => {
		expect(() => { new User({login: "sergei", email: 300}) }).toThrow(TypeError);
	})

});