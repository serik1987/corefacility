import {NotImplementedError} from '../../exceptions/model.mjs';
import ListLoader from './ListLoader.jsx';



/** This is the base class for all components that deal with entity lists
 *  The component's job is to receive filter options from the parent or child
 *  components, find all necessary entities using the Entity.find(properties)
 *  method represent them in some children components
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 		@param 	{callback}	onUserAddOpen		This is an asynchronous method that opens
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
 */
export default class ListEditor extends ListLoader{

	constructor(props){
		super(props);
		this.handleAddButton = this.handleAddButton.bind(this);
		this.handleSelectItem = this.handleSelectItem.bind(this);
	}

	/** Must be invoked when the user presses the Add button.
	 *  This is a callback widget for the child component responsible
	 *  for item adding. Don't forget to add this to the button!
	 * 	@param {SyntheticEvent} event the event object
	 *  @return {undefined}
	 */
	async handleAddButton(event){
		if (!this.props.onUserAddOpen){
			throw new TypeError("The onUserAddOpen promise has not been added as props");
		}
		let entity = (await this.props.onUserAddOpen()) || null;
		if (entity === null){
			return;
		}
		this.itemListComponent.addItem(entity);
	}

	/** Handles clicking on a particular entity.
	 *  This is a callback widget for the child component responsible
	 *  for item modification. Don't forget to add this to the ItemList!
	 * 		@param {SyntheticEvent} event the event object
	 * 		@return {undefined}
	 */
	handleSelectItem(event){
		console.log("Editing the user...");
		console.log(event.detail.toString());
	}

}