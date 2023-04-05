import {translate as t} from 'corefacility-base/utils';
import EntityState from 'corefacility-base/model/entity/EntityState';

import ListLoader from './ListLoader';



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
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param 	{callback}	onItemAddOpen			This is an asynchronous method that opens
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
 * 	@param {callback} onItemAddOpen 			This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class ListEditor extends ListLoader{

	constructor(props){
		super(props);
		this.handleAddButton = this.handleAddButton.bind(this);
		this.handleItemAdd = this.handleItemAdd.bind(this);
		this.handleSelectItem = this.handleSelectItem.bind(this);
		this.handleItemRemove = this.handleItemRemove.bind(this);
	}

	/** Must be invoked when the user presses the Add button.
	 *  This is a callback widget for the child component responsible
	 *  for item adding. Don't forget to add this to the button!
	 * 	@param {SyntheticEvent} event the event object
	 *  @return {undefined}
	 */
	async handleAddButton(event){
		this.setState({_isLoading: false, _error: null});
		if (!this.props.onItemAddOpen){
			throw new TypeError("The onItemAddOpen promise has not been added as props");
		}
		let entity = (await this.props.onItemAddOpen()) || null;
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
	async handleSelectItem(event){
		let entity = event.detail || event.value;
		if (entity.state === EntityState.changed){
			try{
				this.reportListFetching();
				await entity.update();
				this.reportFetchSuccess(undefined);
			} catch (error){
				this.reportFetchFailure(error);
			}
		}
		this.itemListComponent.changeItem(entity);
	}

	/**
	 *  Triggers when the user is going to remove the item from the list
	 * 	@async
	 * 	@param {SyntheticEvent} event  the event triggered by the child component
	 */
	async handleItemRemove(event){
		try{
			let entity = event.detail || event.value;
			this.reportListFetching();
			let result = await window.application.openModal('question', {
				'caption': t("Delete confirmation"),
				'prompt': t("Do you really want to delete this resource?"),
			});
			if (!result){
				this.reportFetchSuccess(undefined);
				return;
			}
			await entity.delete();
			this.itemListComponent.removeItem(entity);
			this.reportFetchSuccess(undefined);
		} catch (error){
			this.reportFetchFailure(error);
		}
	}

	/** Renders the item list.
	 *  This function must be invoked from the render() function.
	 */
	renderItemList(){
		let ItemList = this.entityListComponent;
		return (<ItemList
					items={this.itemList}
					isLoading={this.isLoading}
					isError={this.isError}
					ref={this.registerItemList}
					onItemAdd={this.handleItemAdd}
					onItemSelect={this.handleSelectItem}
					onItemRemove={this.handleItemRemove}
				/>);
	}

	/**
	 * 	Triggers when the user tries to add another user to the user list
	 * 	@async
	 * 	@param {Entity} entity 	the entity to be added
	 */
	async handleItemAdd(entity){
		try{
			this.setState({_isLoading: true, _error: null});
			await entity.create();
			this.itemListComponent.addItem(entity);
		} catch (error){
			this.setState({_error: error});
		} finally{
			this.setState({_isLoading: false});
		}
	}

}