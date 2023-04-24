import {NotImplementedError} from 'corefacility-base/exceptions/model';


/**
 *  This is the base class for all tools that can be applied on the map
 */
export default class BaseTool{

	constructor(){
		this._dragging = false;
		this._startSourceX = undefined;
		this._startSourceY = undefined;
		this._startDestinationX = undefined;
		this._startDestinationY = undefined;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		throw new NotImplementedError('get cursorCss');
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		throw new NotImplementedError('get icon');
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		throw new NotImplementedError('tooltip');
	}

	/**
	 * 	Triggers when the user selects a tool
	 * 	@param {FunctionalMapDrawer} drawer that parent class that has invoked the tool
	 * 	@return {boolean} true will cancel selection, false will do nothing
	 */
	selectTool(drawer){
		return false;
	}

	/**
	 * 	Triggered when the user clicks and holds the left mouse button
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseDown(selectionArea){
		this._dragging = true;
		this._startSourceX = selectionArea.sourceX;
		this._startSourceY = selectionArea.sourceY;
		this._startDestinationX = selectionArea.destinationX;
		this._startDestinationY = selectionArea.destinationY;
	}

	/**
	 * 	Triggered when the user moves the mouse over the functional map.
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseMove(selectionArea){
	}

	/**
	 * 	Triggers when the user releases the mouse button or leaves the functional map area.
	 * 	@param {object|null} 	selectionArea	contains the parent FunctionalMapDrawer together with mouse coordinates
	 * 											null when the user suddenly leaves the map area
	 */
	mouseUp(selectionArea){
		this._dragging = false;
		this._startSourceX = this._startSourceY = this._startDestinationX = this._startDestinationY = undefined;
	}

}