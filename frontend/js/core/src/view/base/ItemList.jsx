import * as React from 'react';
import styled from 'styled-components';

import {NotImplementedError} from '../../exceptions/model.mjs';
import EntityPage from '../../model/entity/page.mjs';
import Scrollable from './Scrollable.jsx';


/** This is a base class for all widgets that represent list of entities
 *  Each entity despite of its source must have the 'id' property that reflects the entity unique ID.
 *  It doesn't matter for this particular component whether 'id' is string ID or number ID. Hoever this
 * 	is crucial that two different entities must have different IDs and two copies of the same entity must
 * 	have the same ID (even though they are two different Javascript objects).
 * 
 * 	Props:
 * 		@param {Array of Entity} items 		array of entities that shall be printed here.
 * 											there must be exactly an array: null or EntityPage is not accepted
 * 		@param {callback} onItemSelect		The function calls when the user clicks on a single item in the list
 */
export default class ItemList extends React.Component{

	/** Javascript array of all entities to show. It equals to the 'items' prop for this particular
	 *  class but may be overriden by subclasses of this class.
	 */
	get items(){
		if (this.props.items instanceof EntityPage){
			throw new Error(`Can't use ItemList to output the paginated list. Use PaginatedItemList instead`);
		} else if (this.props.items === null){
			return [];
		} else {
			return this.props.items;
		}
	}

	render(){
		return(<Scrollable>
			{this.renderContent()}
		</Scrollable>);
	}

	/** Renders list of items itself
	 * 	@return {Rect.Component} the rendered component
	 */
	renderContent(){
		let items = this.items;
		let StyledContainer = styled.ul`
			list-style-type: none;
			margin: 0;
			padding: 0;
		`;

		if (items === null){
			throw new TypeError("The items property is always equal to object")
		}
		if (typeof items.map !== "function"){
			throw new TypeError("The items property is always equal to Javascript array");
		}

		return (<StyledContainer>
			{ items.map(item => this.renderItemContent(item)) }
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

}