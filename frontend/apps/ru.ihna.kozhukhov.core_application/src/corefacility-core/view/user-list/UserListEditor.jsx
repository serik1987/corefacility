import {translate as t} from 'corefacility-base/utils';

import User from 'corefacility-base/model/entity/User';

import CoreListEditor from '../base/CoreListEditor';
import UserList from './UserList';


/** CAUTION! Don't change the state properties which name begins from '_' sign directly.
 *  It manages the state. Use another methods instead!
 */
export default class UserListEditor extends CoreListEditor{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return User;
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 *  @param {object} props props that will be used to calculate the filter
	 * 	@param {object} state state that will be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		if (props.q !== null && props.q !== undefined){
			return {profile: 'basic', q: props.q};
		} else {
			return {profile: 'basic'};
		}
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  meet the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 *  @param {object} props the filter props that will be used to calculate the identity
	 * 	@param {object} state the state that will be used to calculate the identity
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		if (props.q !== null && props.q !== undefined){
			return props.q;
		} else {
			return '';
		}
	}

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		return t("Add User");
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		return t("Users");
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return UserList;
	}

}
