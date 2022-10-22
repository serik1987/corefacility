import ListLoader from './ListLoader.jsx';



export default class ListEditor extends ListLoader{

	constructor(props){
		super(props);
		this.handleAddItem = this.handleAddItem.bind(this);
		this.handleSelectItem = this.handleSelectItem.bind(this);
	}

	/** Handles pressing the Add button.
	 *  This is a callback widget for the child component responsible
	 *  for item adding. Don't forget to add this to the button!
	 * 	@param {SyntheticEvent} event the event object
	 *  @return {undefined}
	 */
	handleAddItem(event){
		console.log("Adding new user...");
		console.log(event);
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