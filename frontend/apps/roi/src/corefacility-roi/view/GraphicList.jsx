import {NotImplementedError} from 'corefacility-base/exceptions/model';

import FunctionalMapDrawer from 'corefacility-imaging/view/FunctionalMapDrawer';


/**
 * 	This is a base class that allows the user to interactively manage list on objects on the functional map.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {FunctionalMap}	functionalMap 				The functional map to be downloaded.
 * 	@param {callback} 		onFetchStart 				Tells the parent component that the FunctionalMapDrawer starts
 * 														the map downloading. The callback requires no arguments.
 * 	@param {callback} 		onFetchSuccess 				Tells the parent component that the FunctionalMapDrawer
 * 														finishes the map downloading. The callback requires no arguments
 * 	@param {callback} 		onFetchFailure 				Tells the parent component that the FunctionalMapDrawer
 * 														was failed to download the map. Arguments:
 * 		@param {Error}			error 						A Javascript exception thrown during the map downloading.
 * 	@param {string}			cssSuffix 					Additional CSS clsaases to apply
 * 	@param {boolean} 		inactive 					All buttons and controls of this drawer are inactive
 * 	@param {Array} 			itemList 					List of all items to display
 * 	@param {callback} 		onItemAdd 					Triggers when the user tries to add new item. Asynchronous
 * 	@param {callback} 		onItemChange 				Triggers when the user tries to change the item. Asynchronous
 * 	@param {callback} 		onItemRemove				Triggers when the user tries to remove the item. Asynchronous
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {BaseTool} 		currentTool					Currently selected tool
 * 	@param {Number} 		minValue 					Minimum amplitude
 * 	@param {Number} 		maxValue 					Maximum amplitude
 * 	@param {Number} 		colorBarResolution 			dimensions of the phase axis color bar, px
 * 	@param {Uint8ClampedArray} 	colorBarImage			bitmap for the phase axis color bar
 * 	@param {Number} 		scale 						Currently selected scale.
 * 	@param {String} 		redirect 					Route to redirect to or null if no redirection required
 * 	@param {Array} 			itemList 					List of all items to output
 * 
 */
export default class GraphicList extends FunctionalMapDrawer{

	/**
	 * 	Adds item to the graphic list
	 * 	@param {Entity} entity 			the entity to add
	 */
	addItem(entity){
		this.setState({
			itemList: [...this.state.itemList, entity],
		});
	}

	/**
	 * 	Changes the item in the graphic list
	 * 	@param {Entity} entity 			the entity to change
	 */
	changeItem(entity){
		let items = [...this.state.itemList];
		let entityIndex = items.findIndex(item => item.id === entity.id);
		if (entityIndex !== -1){
			items[entityIndex] = entity;
			this.setState({
				itemList: items,
			})
		}
	}

	/**
	 * 	Removes the item from the graphic list
	 * 	@param {Entity} entity} 		the entity to remove
	 */
	removeItem(entity){
		let items = [...this.state.itemList];
		let entityIndex = items.findIndex(item => item.id === entity.id);
		if (entityIndex !== -1){
			items.splice(entityIndex, 1);
			this.setState({itemList: items});
		}
	}

	/**
	 * 	Redraws the functional map together with all objects located on it
	 */
	repaint(){
		super.repaint();
		this.repaintItems();
	}

	/**
	 * 	Repaints all items in the list
	 */
	repaintItems(){
		let currentItem = null;
		if (this.state.currentTool && this.state.currentTool.current){
			currentItem = this.state.currentTool.current;
		}

		if (this.state.itemList){
			for (let item of this.state.itemList){
				if (!currentItem || item.id !== currentItem.id){
					this.repaintItem(item, false);
				}
			}
		}

		if (currentItem){
			this.repaintItem(currentItem, true);
		}
	}

	/**
	 * 	Repaints a single item
	 * 	@param {Entity}		item 						An item to repaint
	 * 	@param {boolean} 	isCurrent 					The item is currently selected by a given tool
	 */
	repaintItem(item, isCurrent){
		throw new NotImplementedError('repaintItem');
	}

	/**
	 * 	Triggers when the user tries to add an item. This method must be invoked by one of the tools
	 * 	@async
	 * 	@param {Entity}		entity 						The item added by the user.
	 */
	async handleItemAdd(entity){
		if (this.props.onItemAdd){
			await this.props.onItemAdd(entity);
		}
	}

	/**
	 * 	Triggers when the user tries to modify the ROI.
	 * 	@async
	 * 	@param {Entity} 	entity 						The item to modify
	 */
	async handleItemChange(entity){
		if (this.props.onItemChange){
			let event = {
				target: this,
				detail: entity,
			}
			await this.props.onItemChange(event);
		}
	}

	/**
	 * 	Triggers when the user tries to remove the ROI.
	 */
	async handleItemRemove(entity){
		if (this.props.onItemRemove){
			let event = {
				target: this,
				detail: entity,
			}
			await this.props.onItemRemove(event);
		}
	}

	componentDidUpdate(prevProps, prevState){
		super.componentDidUpdate(prevProps, prevState);
		if (prevProps.itemList !== this.props.itemList){
			this.setState({itemList: this.props.itemList});
		}
	}

}