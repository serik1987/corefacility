import Module from 'corefacility-base/model/entity/Module';
import {StringField} from 'corefacility-base/model/fields';



/** Provides serialization, deserialization and validation for the Google settings
 * 	form
 */
export default class GoogleAuthorizationModule extends Module{

	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			'client_id': new StringField()
				.setDescription("Client ID"),
			'client_secret': new StringField()
				.setDescription("Client Secret")
		}
	}

}