import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as AddIcon} from 'corefacility-base/shared-view/icons/add.svg';

import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';

import RectangularRoi from 'corefacility-roi/model/RectangularRoi';


/**
 * 	The tool allows the user to add new Rectangular ROI
 */
export default class RoiAddTool extends BaseTool{

	constructor(){
		super();
		this._currentCursor = 'move'
		this._roi = null;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Add new rectangular ROI");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <AddIcon/>;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		return this._currentCursor;
	}

	/**
	 * 	Current ROI to add.
	 */
	get current(){
		return this._roi;
	}

	/**
	 * 	Triggered when the user moves the mouse over the functional map.
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseMove(selectionArea){
		if (this._dragging){
			if (selectionArea.sourceX > this._startSourceX && selectionArea.sourceY > this._startSourceY){
				this._currentCursor = 'se-resize';
			} else if (selectionArea.sourceX < this._startSourceX && selectionArea.sourceY > this._startSourceY){
				this._currentCursor = 'sw-resize';
			} else if (selectionArea.sourceX > this._startSourceX && selectionArea.sourceY < this._startSourceY){
				this._currentCursor = 'ne-resize';
			} else if (selectionArea.sourceX < this._startSourceX && selectionArea.sourceY < this._startSourceY){
				this._currentCursor = 'nw-resize';
			}

			let left = Math.round(Math.min(this._startSourceX, selectionArea.sourceX));
			let right = Math.round(Math.max(this._startSourceX, selectionArea.sourceX));
			let top = Math.round(Math.min(this._startSourceY, selectionArea.sourceY));
			let bottom = Math.round(Math.max(this._startSourceY, selectionArea.sourceY));
			if (left === right || top === bottom){
				this._roi = null;
			} else if (this._roi === null) {
				this._roi = new RectangularRoi(
					{left: left, top: top, right: right, bottom: bottom},
					window.application.functionalMap
				);
			} else {
				this._roi.left = left;
				this._roi.top = top;
				this._roi.right = right;
				this._roi.bottom = bottom;
			}
			selectionArea.parent.repaint();
		} else {
			this._currentCursor = 'move';
		}
	}

	/**
	 * 	Triggers when the user releases the mouse button or leaves the functional map area.
	 * 	@param {object|null} 	selectionArea	contains the parent FunctionalMapDrawer together with mouse coordinates
	 * 											null when the user suddenly leaves the map area
	 */
	mouseUp(selectionArea){
		super.mouseUp(selectionArea);
		selectionArea.parent.handleItemAdd(this._roi)
			.finally(() => {
				this._roi = null;
			});
	}

}