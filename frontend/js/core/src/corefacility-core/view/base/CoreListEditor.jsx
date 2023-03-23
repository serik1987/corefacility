import {NotImplementedError} from 'corefacility-base/exceptions/model';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import ListEditor from 'corefacility-base/view/ListEditor';
import CoreWindowHeader from './CoreWindowHeader';


/** This is a base class for user, project and group list editors
 *  styled in the following way:
 * 		- Add entity button is at the top-right corner;
 * 		- The list editor starts from header;
 *      - error / loading / information message is at the top of the editor;
 *      - list of entities satisfying given conditions is below
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 		@param 	{callback}	onItemAddOpen		This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 * 		@param {callback} onItemSelect			This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 		@param {callback} onItemRemove 			This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class CoreListEditor extends ListEditor{

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		throw new NotImplementedError("get addItemButtonName");
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		throw new NotImplementedError("get listHeader");
	}

	render(){

		return (
			<CoreWindowHeader
				isLoading={this.isLoading}
				isError={this.isError}
				error={this.error}
				header={this.listHeader}
				aside={
                    this.addItemButtonName && 
					<PrimaryButton onClick={this.handleAddButton} type="submit" inactive={this.isLoading}>
						{ this.addItemButtonName }
					</PrimaryButton>
				}
				>
					{ this.renderItemList() }
			</CoreWindowHeader>
		);

	}

}