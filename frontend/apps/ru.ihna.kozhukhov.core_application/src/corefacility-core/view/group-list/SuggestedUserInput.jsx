import UserInput from 'corefacility-core/view/user-list/UserInput';


/** Allows some user to select another user not added to a given group.
 * 
 * 	Props:
 *  --------------------------------------------------------------------------------------------------------------------
 * 	@param {Group} group 				Group which users shall not be added
 * 
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
export default class SuggestedUserInput extends UserInput{

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		throw new Error("Not applicable. Use 'group' props.");
	}

	/**
	 * Downloads the entity list from the Web server
	 * @param {oject} filter 		Filter options to be applied
	 * 								(These options will be inserted to the )
	 */
	async _fetchList(filter){
		return await this.props.group.getSuggestedUsers(filter);
	}

}