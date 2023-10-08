import EntityInput from 'corefacility-base/view/EntityInput';

import User from 'corefacility-base/model/entity/User';

import UserInputList from './UserInputList';


/** Allows some user to select another user from the drop-down list.
 * 
 * 	Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {boolean} inactive           if true, the input box will be inactive and hence will not expand or contract
 *                                      the item box.
 * 
 *  @param {boolean} disabled           When the input box is disabled, it is colored as disabled and the user can't
 *                                      enter any value to it.
 * 
 *  @param {string} error               The error message that will be printed when validation fails
 * 
 *  @param {string} tooltip             Detailed description of the field
 * 
 *  @param {string} placeholder         The input placeholder
 * 
 * 	@param {callback} onItemSelect 		Triggers when the user select another user
 * 	--------------------------------------------------------------------------------------------------------------------
 *  
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} searchTerm A search hint entered by the user. The drop-down list will contain some users which
 * 	surname, name or login contains such a search hint.
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class UserInput extends EntityInput{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return User;
	}

	/** Uses the component props (and probably state?) to identify the filter. 
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let filter =  {profile: "light"};
		if (state.searchTerm !== null && state.searchTerm !== undefined){
			filter.q = state.searchTerm;
		}
		return filter;
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		let identity = null;
		if (state.searchTerm !== null && state.searchTerm !== undefined){
			identity = state.searchTerm;
		}
		return identity;
	}

	/** Returns the component where list of entities will be printed.
	 *  This is assumed that the component has 'items' prop
	 */
	get entityListComponent(){
		return UserInputList;
	}

	/**
	 * 	Returns a string that will be put into an input box when the user clicks on it.
	 */
	getEntityIdentity(user){
		return user.surname || user.login;
	}

}