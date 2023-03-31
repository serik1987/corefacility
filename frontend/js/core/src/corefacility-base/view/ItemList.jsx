import * as React from 'react';
import styled from 'styled-components';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import EntityPage from 'corefacility-base/model/EntityPage';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';


/** This is a base class for all widgets that represent list of entities
 *  Each entity despite of its source must have the 'id' property that reflects the entity unique ID.
 *  It doesn't matter for this particular component whether 'id' is string ID or number ID. Hoever this
 * 	is crucial that two different entities must have different IDs and two copies of the same entity must
 * 	have the same ID (even though they are two different Javascript objects).
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {iterable|null} 	items 			The item list, as it passed by the parent component.
 * 											Can be any iterable component. However, subtypes may require instance
 * 											of a certain class
 * 	@param {boolean} 		isLoading		true if the parent component is in 'loading' state.
 * 	@param {boolean} 		isError			true if the parent component is failed to reload this item list.
 * 	@param {callback} 		onItemSelect	The function calls when the user clicks on a single item in the list
 * 											(optional)
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array} 			itemArray 		The item list transformed by the component to the Javascript array,
 * 											and hence can be mapped into array of ListItem components during the
 * 											rendering. Such a list contains not only those enitities that have been
 * 											passed during the reloading but also those passed during creation of
 * 											deletion of items.
 */
export default class ItemList extends React.Component{

	constructor(props){
		super(props);
		this.registerScroll = this.registerScroll.bind(this);
		this.scrollComponent = null;

		this.state = {
			itemArray: [],
		}
	}

	/** @return {boolean} true if downloading the next page is still in progress, false otherwise */
	get isLoading(){
		return this.props.isLoading;
	}

	/** @return {boolean} true if either parent or current component failed to fetch the data */
	get isError(){
		return this.props.isError;
	}

	/** Moves all entities from the items props to the itemArray state, converting their container object
	 *  to Javascript array, if necessary
	 *  	@param {boolean} isAppend	true, if props items must be added to the existent ones,
	 * 									false if props items must replace the existent ones.
	 * 		@return {undefined}
	 */
	liftDown(isAppend = false){
		let newItemArray;

		if (this.props.items === null || this.props.items === undefined){
			newItemArray = [];
		} else if (isAppend){
			newItemArray = [...this.state.itemArray, ...this.props.items];
		} else {
			newItemArray = [...this.props.items];
		}

		this.setState({itemArray: newItemArray});
	}

	/** Registers the scroll bar
	 * 		@param {React.Component} the scroll bar component
	 */
	registerScroll(scrollComponent){
		this.scrollComponent = scrollComponent;
	}

	/** Adds new entity at the beginning of the item list.
	 * 	@param {Entity} the entity to add.
	 * 
	 */
	addItem(entity, prepend=true){
		entity.tag = "recentlyAdded";
		if (prepend){
			this.setState({
				itemArray: [entity, ...this.state.itemArray],
			});
			this.scrollComponent.scroll(0, 0);
		} else {
			this.setState({
				itemArray: [...this.state.itemArray, entity],
			});
			this.scrolLComponent.scroll(0, Infinity);
		}
	}

	/**
	 * Removes the entity from the list
	 * @param {Entity} entity the entity to be removed
	 */
	removeItem(entity){
		let entityIndex = this.state.itemArray.indexOf(entity);
		if (entityIndex !== -1){
			this.state.itemArray.splice(entityIndex, 1);
		}
		this.setState({
			itemArray: [...this.state.itemArray],
		});
	}

	/**
     * Triggers when the user is trying to remove the item
     *  @param {SyntheticEvent} event   the event invoked by the 'Remove' button
     *  @param {Entity} item            a group to be removed
     */
    handleRemove(event, item){
        event.detail = item;
        if (this.props.onItemRemove){
            this.props.onItemRemove(event);
        }
    }

	render(){
		return (<Scrollable ref={this.registerScroll}>
			{this.renderContent()}
		</Scrollable>);
	}

	/** Renders list of items itself
	 * 	@return {Rect.Component} the rendered component
	 */
	renderContent(){
		let StyledContainer = styled.ul`
			list-style-type: none;
			margin: 0;
			padding: 0;
		`;

		if (this.state.itemArray === null){
			throw new TypeError("The items property is always equal to object")
		}

		return (<StyledContainer>
			{ this.state.itemArray.map(item => this.renderItemContent(item)) }
		</StyledContainer>);
	}

	/** Renders content where single item will be shown
	 * 	@param {Entity} item the item to show in this content.
	 *  @return {Rect.Component} the component to render. The component must be a single
	 * 			item with the following conditions met:
	 * 				- the component must be an instance of the ListItem
	 * 				- its root element must be <li>
	 * 				- its key prop must be equal to item.id
	 * 				- its onClick prop must be equal to this.props.onItemSelect
	 */
	renderItemContent(item){
		throw new NotImplementedError("renderItemContent");
	}

	componentDidMount(){
		if (this.props.items !== null){
			this.liftDown();
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.items !== prevProps.items){
			this.liftDown();
		}
	}

}