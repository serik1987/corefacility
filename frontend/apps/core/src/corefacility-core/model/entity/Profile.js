import {ReadOnlyField} from 'corefacility-base/model/fields';
import FileField from 'corefacility-base/model/fields/FileField';
import User from './User';
import ProfileProvider from 'corefacility-core/model/providers/ProfileProvider';
import PasswordField from 'corefacility-core/model/fields/PasswordField';


/** The model is used to represent the current user profile
 * 
 *  Fields:
 * 		@param {int} id 				 unique user identifier
 * 		@param {string} login			 small alias that will be used for the standard authorization
 * 		@param {boolean} is_password_set true if the password has been set and delivered to the user
 *                                       false if not. In this case the user can't be authorized
 * 		@param {string} name			 The user's first name (to be used for visualization)
 * 		@param {string} surname			 The user's last name (to be used for visualization)
 * 		@param {string} e-mail			 The user's e-mail (to be used for the password recovery system)
 * 		@param {string} phone			 The user's phone number (to be called in case of suspicious operations)
 * 		@param {string} unix_group		 name of the POSIX account corresponding to the user
 * 		@param {string} home_dir		 directory where user personal files were located
 * 
 * Entity providers:
 * 		HttpRequestProvider - information exchange with the Web Server
 */
export default class Profile extends User{

    static get _entityName(){
        return "Current user";
    }

    /**
     * Describes all profile fields
     * @return {array of Field}         All entity fields containing in the user profile
     */
    static _definePropertyDescription(){
        let properties = User._definePropertyDescription();
        properties.login = new ReadOnlyField().setDescription("Login");
        delete properties['is_password_set'];
        properties.is_locked = new ReadOnlyField().setDescription("Is user locked");
        properties.is_superuser = new ReadOnlyField().setDescription("Has administration rights");
        properties.is_support = new ReadOnlyField().setDescription("Is support user");
        properties.avatar = new FileField(entity => 'profile/avatar/')
                .setDescription("User's avatar");
        properties.password = new PasswordField().setDescription("User's password");
        return properties;
    }

    /**
     * Gets list of all entity providers
     * @return {array of EntityProviders} all entity providers used
     */
    static _defineEntityProviders(){
        return [new ProfileProvider(Profile)];
    }

    /** Returns a copy of the entity downloaded from the server
     *  @async
     *  @return {Entity} the entity copy
     */
    async reload(){
        window.application.user = await super.reload();
        return window.application.user;
    }

}
