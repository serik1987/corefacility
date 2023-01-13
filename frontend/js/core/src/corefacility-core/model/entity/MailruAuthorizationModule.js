import Module from 'corefacility-base/model/entity/Module';
import {StringField} from 'corefacility-base/model/fields';
import DurationField from 'corefacility-base/model/fields/DurationField';


/** Provides settings for the Mail.Ru authorization module */
export default class MailruAuthorizationModule extends Module{

	static _definePropertyDescription(){
		return {
			...Module._definePropertyDescription(),
			client_id: new StringField()
				.setDescription("Client ID"),
			client_secret: new StringField()
				.setDescription("Client Secret"),
			expiry_term: new DurationField()
				.setDescription("State ID expiry term"),
		}
	}

}